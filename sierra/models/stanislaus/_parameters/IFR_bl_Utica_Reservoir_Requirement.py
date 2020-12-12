from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Utica_Reservoir_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 0.14158 #cms(5 cfs)
        if self.mode == 'planning':
            ifr_val *= self.days_in_month
        return ifr_val

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Utica_Reservoir_Requirement.register()