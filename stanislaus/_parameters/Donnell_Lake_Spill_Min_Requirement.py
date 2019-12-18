import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class Donnell_Lake_Spill_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT_table = self.model.tables["WYT P2005 & P2130"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1
        WYT = WYT_table[operational_water_year]

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        ifr_val = 0.0

        # Calculate supp IFR
        data_supp = self.model.tables["Supplemental IFR below Donnell Lake"]

        month = self.datetime.month

        if self.model.mode == 'scheduling':

            if month == 10 and self.datetime.day == 1:
                self.peak_dt = self.model.tables["Peak Donnells Runoff"][timestep.year + 1]
            diff_day = (self.datetime - self.peak_dt).days - 1
            if 0 <= diff_day < 91:
                days_idx = diff_day - diff_day % 7
                ifr_supp = data_supp.at[days_idx, WYT] / 35.315
                ifr_val += ifr_supp
                ifr_val = self.get_down_ramp_ifr(timestep, ifr_val, initial_value=ifr_val, rate=0.25)

        elif WYT > 1:
            if month == 5:
                ifr_supp = data_supp.loc[0:28, WYT].mean()
            elif month == 6:
                ifr_supp = data_supp.loc[35:56, WYT].mean()
            elif month == 7:
                ifr_supp = data_supp.loc[63:84, WYT].mean()
            else:
                ifr_supp = 0.0

            ifr_val += ifr_supp / 35.31

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


Donnell_Lake_Spill_Min_Requirement.register()
print(" [*] IFR_bl_Donnell_Lake_Min_Requirement successfully registered")
