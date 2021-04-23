from sierra.base_parameters import FlowRangeParameter

from sierra.utilities.converter import convert


class IFR_bl_Philadelphia_Div_Max_Requirement(FlowRangeParameter):
    """"""

    def _value(self, timestep, scenario_index):
        max_flow = 50 / 35.31  # IFR max is 60 cfs; 50 cfs in practice
        if self.model.mode == 'scheduling':
            ifr_range = self.get_ifr_range(
                timestep, scenario_index,
                initial_value=(10 / 35.31), max_flow=max_flow, rate=3.0)
        else:
            ifr_range = self.get_ifr_range(
                timestep, scenario_index, max_flow=max_flow, rate=6.0)
        return ifr_range

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Philadelphia_Div_Max_Requirement.register()
