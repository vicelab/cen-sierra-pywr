import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Goodwin_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        wyt = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        df = self.read_csv("Management/BAU/IFRs/IFR_Below Goodwin Dam_cfs_daily.csv", names=[1, 2, 3, 4, 5], header=0)
        start = self.datetime.strftime('%b-%d')
        if self.model.mode == 'scheduling':
            return df.at[start, wyt] / 35.31  # convert cfs to mcm
        else:
            days_in_month = self.days_in_month()
            end = '{}-{:02}'.format(start.split('-')[0], days_in_month)
            return df[wyt][start:end].sum() / 35.31

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
