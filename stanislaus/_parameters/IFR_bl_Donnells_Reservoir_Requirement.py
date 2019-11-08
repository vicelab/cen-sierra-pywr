import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Donnells_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = str(self.get("WYT_SJValley"))
        management = "BAU"
        path = "Management/{mgt}/IFRs/".format(mgt=management)
        if timestep.index == 0:
            if self.mode == 'scheduling':
                fName = 'IFR_Below Donnells Reservoir (MIF)_cfs_daily.csv'
            else:
                fName = 'IFR_Below Donnells Reservoir (MIF)_cfs_monthly.csv'
            self.data_ifr = self.read_csv(path + fName, usecols=[0, 1, 2, 3, 4, 5, 6], index_col=None, header=0,
                                          names=['start_date', 'end_date', '1', '2', '3', '4', '5'], parse_dates=[0, 1])

        if timestep.datetime.month >= 10:
            dt = datetime.date(1999, timestep.month, timestep.day)
        else:
            dt = datetime.date(2000, timestep.month, timestep.day)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        # Calculate regular IFR
        df = self.data_ifr
        ifr_val = df[(df['start_date'] <= dt) & (df['end_date'] >= dt)][WYT]
        ifr_val *= self.cfs_to_cms

        # Calculate supp IFR
        data_supp = self.read_csv(path + 'IFR_Below Donnells Reservoir (Supp)_cfs_daily.csv',
                                  names=['Day_st', 'Day_end', '1', '2', '3', '4', '5'], header=0, index_col=None)
        if self.mode == 'scheduling':
            if timestep.index == 0:
                path = 'Scenarios/Livneh/preprocessed/peak_runoff_DonnellsRes_MarToMay_cms.csv'
                self.peak_inflow_Donnells = self.read_csv(path, usecols=[0, 1], index_col=[0], parse_dates=[1],
                                                          squeeze=True)  # cms

            if timestep.month == 10 and timestep.day == 1:
                self.peak_dt = self.peak_inflow_Donnells[timestep.year + 1]
            diff_day = (timestep.datetime - self.peak_dt).days
            ifr_supp = 0

            if 0 < diff_day < 91:
                ifr_supp = \
                    (data_supp[(data_supp['Day_st'] < diff_day) & (diff_day <= data_supp['Day_end'])][WYT]).values[-1]
                ifr_supp *= self.cfs_to_cms
            return ifr_val + ifr_supp

        else:
            if timestep.month == 5:
                ifr_supp = data_supp[WYT].loc[0:4].mean()
            elif timestep.month == 6:
                ifr_supp = data_supp[WYT].loc[5:8].mean()
            elif timestep.month == 7:
                ifr_supp = data_supp[WYT].loc[8:12].mean()
            else:
                ifr_supp = 0
        return ifr_val + ifr_supp

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


IFR_bl_Donnells_Reservoir_Requirement.register()
print(" [*] IFR_bl_Donnells_Reservoir_Requirement successfully registered")
