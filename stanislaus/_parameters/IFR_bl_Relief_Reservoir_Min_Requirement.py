import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Relief_Reservoir_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.model.tables["WYT P2005 & P2130"][self.operational_water_year]
        schedule = self.model.tables["IFR Below Relief Reservoir schedule"]

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
            ifr_cms = self.get_down_ramp_ifr(timestep, ifr_cms, rate=0.25)

        else:
            ifr_cms = schedule.at[(month, 1), WYT] / 35.31 * self.days_in_month()

        return ifr_cms

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


IFR_bl_Relief_Reservoir_Min_Requirement.register()
print(" [*] IFR_bl_Relief_Reservoir_Min_Requirement successfully registered")
