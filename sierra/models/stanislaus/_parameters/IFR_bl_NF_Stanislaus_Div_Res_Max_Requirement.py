from sierra.base_parameters import FlowRangeParameter

from sierra.utilities.converter import convert


class IFR_bl_NF_Stanislaus_Div_Res_Max_Requirement(FlowRangeParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 16.5 / 35.31  # cfs to cms (16.5 cfs)
        if self.model.mode == 'scheduling':
            ifr_range = self.get_ifr_range(timestep, scenario_index, initial_value=ifr_val, rate=0.20)
        else:
            ifr_range = 1e6
        return ifr_range

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_NF_Stanislaus_Div_Res_Max_Requirement.register()
