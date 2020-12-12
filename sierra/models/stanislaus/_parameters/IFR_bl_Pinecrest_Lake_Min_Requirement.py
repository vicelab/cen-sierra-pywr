from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Pinecrest_Lake_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.model.tables["WYT P2005 & P2130"].get(self.operational_water_year, 3)
        schedule = self.model.tables["IFR Below Pinecrest Lake schedule"]

        month = self.datetime.month
        if self.model.mode == 'scheduling':
            day = self.datetime.day
            start_day = 1
            start_month = month
            if (2, 10) <= (month, day) <= (5, 31):
                start_day = 10
            if month in [2, 3, 4, 5] and day <= 9:
                start_month -= 1
            ifr_cms = schedule.at[(start_month, start_day), WYT] / 35.31
            ifr_cms = self.get_down_ramp_ifr(timestep, scenario_index, ifr_cms, rate=0.25)

        else:
            ifr_cms = schedule.at[(month, 1), WYT] / 35.31 * self.days_in_month

        return ifr_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Pinecrest_Lake_Min_Requirement.register()
