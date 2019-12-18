import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Philadelphia_Div_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT_table = self.model.tables["WYT P2005 & P2130"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1

        WYT = WYT_table[operational_water_year]
        ifr_val = {1: 0, 2: 10, 3: 10, 5: 15}.get(WYT)
        if not ifr_val:
            month = self.datetime.month
            day = self.datetime.day
            if (4, 10) <= (month, day) <= (11, 30):
                ifr_val = 15
            elif self.model.mode == 'planning' and (month, day) == (4, 1):
                ifr_val = 13.5
            else:
                ifr_val = 10

        ifr_val /= 35.31

        if self.model.mode == 'scheduling':
            ifr_val = self.get_down_ramp_ifr(timestep, ifr_val, initial_value=10 / 35.31, rate=0.25)

        elif self.model.mode == 'planning':
            ifr_val *= self.days_in_month()

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
