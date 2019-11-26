import datetime
from parameters import WaterLPParameter

from utilities.converter import convert

from dateutil.relativedelta import relativedelta


class IFR_bl_Goodwin_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix)
        df = self.read_csv("Management/BAU/IFRs/IFR_Below Goodwin Dam_cfs_daily.csv", names=[1, 2, 3, 4, 5], header=0)
        start = self.datetime.strftime('%b-%d')
        if self.model.mode == 'scheduling':
            min_ifr = df.at[start, WYT] / 35.31  # cfs to cms
        else:
            end = (self.datetime + relativedelta(days=self.days_in_month() - 1)).strftime('%b-%d')
            min_ifr = df[WYT][start:end].sum() / 35.31  # cfs to cms

        return min_ifr

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Goodwin_Reservoir_Requirement.register()
print(" [*] IFR_bl_Goodwin_Reservoir_Requirement successfully registered")
