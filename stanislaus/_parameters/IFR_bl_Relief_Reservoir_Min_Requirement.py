import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Relief_Reservoir_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1

        WYT = self.model.tables["WYT P2005 & P2130"][operational_water_year]

        schedule = self.model.tables["IFR Below Relief Reservoir schedule"]
        if self.datetime.month >= 10:
            dt = datetime.date(1999, self.datetime.month, self.datetime.day)
        else:
            dt = datetime.date(2000, self.datetime.month, self.datetime.day)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        ifr_val = schedule[(schedule['start_date'] <= dt) & (schedule['end_date'] >= dt)][str(WYT)].values[-1] / 35.314666 # cfs to cms

        # apply down ramp rate
        if self.model.mode == 'scheduling':
            ifr_val = self.get_down_ramp_ifr(timestep, ifr_val, initial_value=30/35.31, rate=0.25)

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


IFR_bl_Relief_Reservoir_Min_Requirement.register()
print(" [*] IFR_bl_Relief_Reservoir_Min_Requirement successfully registered")
