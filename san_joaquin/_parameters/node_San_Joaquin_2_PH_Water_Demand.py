from parameters import WaterLPParameter

from utilities.converter import convert

class node_San_Joaquin_2_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return self.get("node/San Joaquin 2 PH/Turbine Capacity", **kwargs)
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_San_Joaquin_2_PH_Water_Demand.register()
print(" [*] node_San_Joaquin_2_PH_Water_Demand successfully registered")
