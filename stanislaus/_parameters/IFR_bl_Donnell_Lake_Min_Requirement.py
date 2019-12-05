import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Donnell_Lake_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.get("San Joaquin Valley WYT" + self.month_suffix)
        WYT_str = str(WYT)
        schedule = self.model.tables["IFR Below Donnell Lake schedule"]

        if self.datetime.month >= 10:
            dt = datetime.date(1999, self.datetime.month, self.datetime.day)
        else:
            dt = datetime.date(2000, self.datetime.month, self.datetime.day)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        ifr_val = schedule[(schedule['start_date'] <= dt) & (schedule['end_date'] >= dt)][WYT_str].values[-1] / 35.31

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
