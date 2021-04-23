from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Collierville_PH_discharge_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.mode == 'scheduling':
            # get previous flow
            initial_value = 0
            if timestep.index == 0:
                initial_value = 0.4 / 0.0846 # cms
            min_ifr = self.get_down_ramp_ifr(timestep, scenario_index, 0.0, initial_value=initial_value, rate=0.25)

        if self.mode == 'planning':
            # no constraint
            min_ifr = 0.0
        return min_ifr

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Collierville_PH_discharge_Min_Requirement.register()
