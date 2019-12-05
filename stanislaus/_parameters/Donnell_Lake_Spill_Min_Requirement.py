import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class Donnell_Lake_Spill_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.get("San Joaquin Valley WYT" + self.month_suffix)
        WYT_str = str(WYT)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        ifr_val = 0.0

        # Calculate supp IFR
        data_supp = self.model.tables["Supplemental IFR below Donnell Lake"]

        if self.mode == 'scheduling':
            if self.datetime.month == 10 and self.datetime.day == 1:
                self.peak_dt = self.model.tables["Peak Donnells Runoff"][timestep.year + 1]
            diff_day = (timestep.datetime - self.peak_dt).days
            ifr_supp = 0

            if 0 < diff_day < 91:
                ifr_supp = \
                    (data_supp[(data_supp['Day_st'] < diff_day) & (diff_day <= data_supp['Day_end'])][WYT_str]).values[
                        -1]
                ifr_supp *= self.cfs_to_cms
            ifr_val += ifr_supp
            ifr_val = self.get_down_ramp_ifr(timestep, ifr_val, initial_value=ifr_val, rate=0.25)

        else:
            if self.datetime.month == 5:
                ifr_supp = data_supp[WYT_str].loc[0:4].mean()
            elif self.datetime.month == 6:
                ifr_supp = data_supp[WYT_str].loc[5:8].mean()
            elif self.datetime.month == 7:
                ifr_supp = data_supp[WYT_str].loc[8:12].mean()
            else:
                ifr_supp = 0

            ifr_val += ifr_supp

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
