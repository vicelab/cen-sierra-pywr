from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Angels_Div_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 0.14158 * 1.1  # cms (5 cfs) w/ 10% factor of safety
        # if self.model.mode == 'scheduling':
        #     # IFR is max of 75% of previous flow Qp and IFR
        #     if timestep.index == 0:
        #         Qp = ifr_val
        #     else:
        #         Qp = self.model.nodes[self.res_name].prev_flow[scenario_index.global_id] / 0.0864  # convert to cms
        #     ifr_val = max(ifr_val, Qp * 0.75)
        # else:
        #     ifr_val *= self.days_in_month
        if self.model.mode == 'planning':
            ifr_val *= self.days_in_month
        return ifr_val

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Angels_Div_Min_Requirement.register()
