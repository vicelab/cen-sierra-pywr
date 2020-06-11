from pywr.recorders import NumpyArrayNodeRecorder
from pywr.parameters import load_parameter, load_parameter_values
import numpy as np
import pandas as pd


def hydropower_calculation(flow, head, efficiency,
                           flow_unit_conversion=1.0, energy_unit_conversion=1e-6,
                           density=1000.0):
    """
    Calculate the total power produced using the hydropower equation.
    
   
    Parameters
    ----------
    flow : double 
        Flow rate of water through the turbine. Should be converted using `flow_unit_conversion` to 
        units of $m^3£ per day (not per second).
    head : double
        Working head of the turbine (water surface elevation - tailwater elevation).
    efficiency : double
        An efficiency scaling factor for the power output of the turbine.
    flow_unit_conversion : double (default=1.0)
        A factor used to transform the units of flow to be compatible with the equation here. This
        should convert flow to units of $m^3/day$
    energy_unit_conversion : double (default=1e-6)
        A factor used to transform the units of power. Defaults to 1e-6 to return $MJ$/day. 
    density : double (default=1000)
        Density of water in $kgm^{-3}$.
        
    Returns
    -------
    power : double
        Hydropower production rate in units of energy per day.
    
    Notes
    -----
    The hydropower calculation uses the following equation.
    
    .. math:: P = \rho * g * \deltaH * q
    
    The flow rate in should be converted to units of :math:`m^3` per day using the `flow_unit_conversion` parameter.    
    
    """

    # Convert flow to correct units (typically to m3/day)
    q = flow * flow_unit_conversion
    # Power
    power = density * q * 9.81 * head * efficiency

    return power * energy_unit_conversion


class HydropowerEnergyRecorder(NumpyArrayNodeRecorder):
    """ Calculates the power production using the hydropower equation

    This recorder saves an array of the hydrpower production in each timestep. It can be converted to a dataframe
    after a model run has completed. It does not calculate total energy production.

    Parameters
    ----------

    water_elevation_parameter : Parameter instance (default=None)
        Elevation of water entering the turbine. The difference of this value with the `tailwater_elevation` gives
        the working head of the turbine.
    tailwater_elevation : double
        Elevation of the turbine itself. The difference between the `water_elevation` and this value gives
        the working head of the turbine.
    efficiency : float (default=1.0)
        The efficiency of the turbine.
    density : float (default=1000.0)
        The density of water.
    flow_unit_conversion : float (default=1.0)
        A factor used to transform the units of flow to be compatible with the equation here. This
        should convert flow to units of :math:`m^3/day`
    energy_unit_conversion : float (default=1e-6)
        A factor used to transform the units of total energy. Defaults to 1e-6 to return :math:`MJ`.

    Notes
    -----
    The hydropower calculation uses the following equation.

    .. math:: P = \\rho * g * \\delta H * q

    The flow rate in should be converted to units of :math:`m^3` per day using the `flow_unit_conversion` parameter.

    Head is calculated from the given `water_elevation_parameter` and `tailwater_elevation` value. If water elevation
    is given then head is the difference in elevation between the water and the turbine. If water elevation parameter
    is `None` then the head is simply the turbine elevation.


    See Also
    --------
    TotalHydroEnergyRecorder
    pywr.parameters.HydropowerTargetParameter

    """

    def __init__(self, model, node, water_elevation_parameter=None, water_elevation_reservoir=None,
                 tailwater_elevation=0.0, efficiency=1.0, density=1000,
                 flow_unit_conversion=1.0, energy_unit_conversion=1e-6, **kwargs):
        super(HydropowerEnergyRecorder, self).__init__(model, node, **kwargs)

        self._water_elevation_parameter = water_elevation_parameter
        self._water_elevation_reservoir = water_elevation_reservoir
        self.tailwater_elevation = tailwater_elevation
        self.efficiency = efficiency
        self.density = density
        self.flow_unit_conversion = flow_unit_conversion
        self.energy_unit_conversion = energy_unit_conversion

    def setup(self):
        ncomb = len(self.model.scenarios.combinations)
        nts = len(self.model.timestepper)
        self._data = np.zeros((nts, ncomb))

    def reset(self):
        self._data[:, :] = 0.0

    def to_dataframe(self):
        """ Return a `pandas.DataFrame` of the recorder data
        This DataFrame contains a MultiIndex for the columns with the recorder name
        as the first level and scenario combination names as the second level. This
        allows for easy combination with multiple recorder's DataFrames
        """
        index = self.model.timestepper.datetime_index
        sc_index = self.model.scenarios.multiindex

        return pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)

    @property
    def water_elevation_parameter(self):
        return self._water_elevation_parameter

    @water_elevation_parameter.setter
    def water_elevation_parameter(self, parameter):
        if self._water_elevation_parameter:
            self.children.remove(self._water_elevation_parameter)
        self.children.add(parameter)
        self._water_elevation_parameter = parameter

    def after(self):
        ts = self.model.timestepper.current

        for scenario_index in self.model.scenarios.combinations:

            if self._water_elevation_parameter is not None:
                if type(self._water_elevation_parameter) in [float, int]:
                    head = self._water_elevation_parameter
                else:
                    head = self._water_elevation_parameter.get_value(scenario_index)
            elif self._water_elevation_reservoir is not None:
                reservoir = self._water_elevation_reservoir
                head = reservoir.get_level(scenario_index)
            else:
                raise ValueError('Either head or water_elevation_parameter/_reservoir must be set.')

            if self.tailwater_elevation is not None:
                head -= self.tailwater_elevation

            # -ve head is not valid
            head = max(head, 0.0)
            # Get the flow from the current node
            flow = self.node.flow[scenario_index.global_id]
            turbine_capacity = self.node.turbine_capacity
            if turbine_capacity is not None:
                if type(turbine_capacity) in [float, int]:
                    pass
                else:
                    turbine_capacity = turbine_capacity.get_value(scenario_index)
                flow = min(flow, turbine_capacity)
            energy = hydropower_calculation(flow, head, self.efficiency, density=self.density,
                                            flow_unit_conversion=self.flow_unit_conversion,
                                            energy_unit_conversion=self.energy_unit_conversion)

            self._data[ts.index, scenario_index.global_id] = energy

    @classmethod
    def load(cls, model, data):
        node = model._get_node_from_ref(model, data.pop("node"))
        water_elevation_reservoir = None
        water_elevation_parameter = None
        if node.water_elevation_reservoir:
            water_elevation_reservoir = model._get_node_from_ref(model, node.water_elevation_reservoir)
        elif node.water_elevation_parameter:
            water_elevation_parameter = load_parameter(model, node.water_elevation_parameter)
        else:
            water_elevation_parameter = node.head

        data['efficiency'] = node.efficiency
        data['tailwater_elevation'] = node.tailwater_elevation

        # For now, we add this flow unit conversion here
        # conversion is from mcm (model) to cms (energy calculation)
        data['flow_unit_conversion'] = 1 / 0.0864

        # For now, we add the energy unit conversion here
        # conversion is from W (J/s) to MWh
        data['energy_unit_conversion'] = 24 / 1e6

        return cls(model, node, water_elevation_parameter=water_elevation_parameter,
                   water_elevation_reservoir=water_elevation_reservoir, **data)

#
# HydropowerRecorder2.register()
