import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Donnell_Lake_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT_table = self.model.tables["WYT P2005 & P2130"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1
        WYT = WYT_table[operational_water_year]

        if WYT <= 2:
            return 25 / 35.31
        elif WYT <= 4:
            if self.datetime.month in [7, 8]:
                return 45 / 35.31
            else:
                return 40 / 35.31

        schedule = self.model.tables["IFR Below Donnell Lake schedule"]

        if self.model.mode == 'scheduling':
            month = timestep.month
            day = timestep.day
            if (2, 10) <= (month, day) <= (5, 31):
                start_day = 10
            else:
                start_day = 1
            if 2 <= month <= 5 and day <= 9:
                start_month = month - 1
            else:
                start_month = month
            start_date = '{}-{}'.format(start_month, start_day)
            ifr_val = schedule.at[start_date, WYT]
        else:
            ifr_val = schedule.at[self.datetime.month, WYT] * self.days_in_month()

        ifr_val /= 35.31  # convert to cms

        return ifr_val

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter "{}" in {} model'.format(self.name, self.model.mode))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Donnell_Lake_Min_Requirement.register()
print(" [*] IFR_bl_Donnell_Lake_Min_Requirement successfully registered")
