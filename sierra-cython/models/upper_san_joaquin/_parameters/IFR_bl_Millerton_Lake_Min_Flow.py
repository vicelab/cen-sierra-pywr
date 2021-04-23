from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Millerton_Lake_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # get WYT index
        if 3 <= self.datetime.month:
            restoration_year = self.datetime.year
        else:
            restoration_year = self.datetime.year - 1

        # get date index
        ifr_schedule_cfs = self.model.tables["IFR Schedule below Friant Dam"]

        # get full natural flow
        # fnf = self.model.tables["Annual Full Natural Flow"][restoration_year]

        if self.model.mode == 'planning':
            date_index = self.datetime.month - 1
        else:
            month_day = (self.datetime.month, self.datetime.day)
            date_index = sum([1 for md in ifr_schedule_cfs.index if month_day >= md]) - 1

        # get IFR from schedule
        wyt = self.model.tables["SJ restoration flows"].at[restoration_year, 'WYT']
        wyt_index = wyt - 1
        ifr_cfs = ifr_schedule_cfs.iat[date_index, wyt_index]
        if wyt in [3, 4, 5]:
            allocation_adjustment = self.model.tables["SJ restoration flows"] \
                .at[restoration_year, 'Allocation adjustment']
            ifr_cfs *= allocation_adjustment

        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month

        return ifr_cfs / 35.31

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Millerton_Lake_Min_Flow.register()
