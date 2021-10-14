from sierra.base_parameters import MinFlowParameter
from sierra.utilities.converter import convert


class IFR_bl_Beardsley_Afterbay_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT = self.get("San Joaquin Valley WYT" + self.month_suffix, timestep, scenario_index)
        if WYT in [1, 2]:  # Critical (1) or Dry (2) years
            ifr_cfs = 50  # cfs
        else:
            ifr_cfs = 135
        ifr_cfs += 5  # 5 cfs safety buffer based on observations
        ifr_cms = ifr_cfs / 35.315  # convert to cms
        if self.model.mode == 'scheduling':
            ifr_cms = self.get_down_ramp_ifr(timestep, scenario_index, ifr_cms, initial_value=140 / 35.31, rate=0.25)
        else:
            ifr_cms *= self.days_in_month
        return ifr_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Beardsley_Afterbay_Min_Requirement.register()
