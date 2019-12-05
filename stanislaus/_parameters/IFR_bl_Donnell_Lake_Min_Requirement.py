import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Donnell_Lake_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT_table = self.model.tables["WYI_P2130"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1

        WYT_str = WYT_table[operational_water_year]
        management = "BAU"
        path = "Management/{mgt}/IFRs/".format(mgt=management)
        if timestep.index == 0:
            if self.model.mode == 'scheduling':
                fName = 'IFR_Below Donnells Reservoir (MIF)_cfs_daily.csv'
            else:
                fName = 'IFR_Below Donnells Reservoir (MIF)_cfs_monthly.csv'
            self.ifr_schedule = self.read_csv(path + fName, usecols=[0, 1, 2, 3, 4, 5, 6], index_col=None, header=0,
                                              names=['start_date', 'end_date', '1', '2', '3', '4', '5'],
                                              parse_dates=[0, 1])

        if self.datetime.month >= 10:
            dt = datetime.date(1999, self.datetime.month, self.datetime.day)
        else:
            dt = datetime.date(2000, self.datetime.month, self.datetime.day)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        df = self.ifr_schedule
        ifr_val = df[(df['start_date'] <= dt) & (df['end_date'] >= dt)][WYT_str].values[-1]
        ifr_val *= self.cfs_to_cms

        # Calculate supp IFR
        data_supp = self.read_csv(path + 'IFR_Below Donnells Reservoir (Supp)_cfs_daily.csv',
                                  names=['Day_st', 'Day_end', '1', '2', '3', '4', '5'], header=0, index_col=None)
        if self.mode == 'scheduling':
            # if timestep.index == 0:
            #     path = 'Scenarios/Livneh/preprocessed/peak_runoff_DonnellsRes_MarToMay_cms.csv'
            #     self.peak_inflow_Donnells = self.read_csv(path, usecols=[0, 1], index_col=[0], parse_dates=[1],
            #                                               squeeze=True)  # cms
            if self.datetime.month == 10 and self.datetime.day == 1:
                # self.peak_dt = self.peak_inflow_Donnells[timestep.year + 1]
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
            return ifr_val

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


IFR_bl_Donnell_Lake_Min_Requirement.register()
print(" [*] IFR_bl_Donnell_Lake_Min_Requirement successfully registered")
