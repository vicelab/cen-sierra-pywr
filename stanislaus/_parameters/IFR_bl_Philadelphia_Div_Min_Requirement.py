import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Philadelphia_Div_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        year = self.datetime.year
        month = self.datetime.month

        WYT = self.model.tables["WYT P2005 & P2130"][self.operational_water_year]
        schedule = self.model.tables["IFR Below Philadelphia Div Schedule"]

        if self.model.mode == 'scheduling':
            day = self.datetime.day
            start_day = 1
            start_month = month
            if (2, 10) <= (month, day) <= (5, 31):
                start_day = 10
            if month in [2, 3, 4, 5] and day <= 9:
                start_month -= 1

            ifr_val = schedule.at[(start_month, start_day), WYT] / 35.31
            ifr_val = self.get_down_ramp_ifr(timestep, ifr_val, rate=0.25)

        else:
            ifr_val = schedule.at[month, WYT] / 35.31 * self.days_in_month()

        return ifr_val

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


IFR_bl_Philadelphia_Div_Min_Requirement.register()
print(" [*] IFR_bl_Philadelphia_Div_Min_Requirement successfully registered")
