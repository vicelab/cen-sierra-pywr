from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class Donnell_Lake_Spill_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # Default WYT is 3, for instances where we don't have pre-calculated WYT for the first operational water year
        # This is needed particularly for sequences.
        WYT = self.model.tables["WYT P2005 & P2130"].get(self.operational_water_year, 3)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        ifr_cms = 0.0

        # Calculate supp IFR
        if self.mode == 'scheduling':

            if self.datetime.month == 10 and self.datetime.day == 1:
                self.peak_dt = self.model.tables["Peak Donnells Runoff"][timestep.year + 1]

            diff_day = (timestep.datetime - self.peak_dt).days
            if 0 <= diff_day < 91:
                data_supp = self.model.tables["Supplemental IFR below Donnell Lake"]
                start_idx = diff_day - diff_day % 7
                ifr_cms += data_supp.at[start_idx, WYT] / 35.31
            ifr_cms = self.get_down_ramp_ifr(timestep, scenario_index, ifr_cms, rate=0.25)

        else:
            data_supp = self.model.tables["Supplemental IFR below Donnell Lake"]
            if self.datetime.month == 5:
                ifr_cfs = data_supp[WYT].iloc[0:4].mean()
            elif self.datetime.month == 6:
                ifr_cfs = data_supp[WYT].iloc[5:8].mean()
            elif self.datetime.month == 7:
                ifr_cfs = data_supp[WYT].iloc[8:12].mean()
            else:
                ifr_cfs = 0

            ifr_cms = (ifr_cms + ifr_cfs / 35.31) * self.days_in_month

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


Donnell_Lake_Spill_Min_Requirement.register()
