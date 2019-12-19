import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Donnell_Lake_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # WYT = self.get("San Joaquin Valley WYT" + self.month_suffix)
        WYT = self.model.tables["WYT P2005 & P2130"][self.operational_water_year]
        schedule = self.model.tables["IFR Below Donnell Lake schedule"][WYT]
        month = self.datetime.month
        if self.model.mode == 'scheduling':
            day = self.datetime.day
            start_day = 1
            start_month = month
            if (2, 10) <= (month, day) <= (5, 31):
                start_day = 10
            if month in [2, 3, 4, 5] and day <= 9:
                start_month -= 1
            ifr_cms = schedule[(start_month, start_day)] / 35.31

        else:
            ifr_cms = schedule[(month, 1)] / 35.31 * self.days_in_month()

        return ifr_cms

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
