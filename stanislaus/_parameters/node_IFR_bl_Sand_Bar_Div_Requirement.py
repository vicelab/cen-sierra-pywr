import datetime
from parameters import WaterLPParameter
from utilities.converter import convert

class node_IFR_bl_Sand_Bar_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = int(self.get("WYI_SJValley"))
        management = "BAU"
        path = "Management/{mgt}/IFRs/".format(mgt=management)
        if self.mode == 'scheduling':
            fName = 'IFR_Below Sand Bar Diversion (MIF)_cfs_daily.csv'
        else:
            fName = 'IFR_Below Sand Bar Diversion (MIF)_cfs_monthly.csv'
        if timestep.datetime.month >= 10:
            dt = datetime.date(1999, timestep.month, timestep.day)
        else:
            dt = datetime.date(2000, timestep.month, timestep.day)

        data = self.read_csv(path + fName, usecols=[0, 1, 2, 3, 4, 5, 6], index_col=None, header=0,
                             names=['start_date', 'end_date', '1', '2', '3', '4', '5'], parse_dates=[0, 1])
        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        ifr_val = (data[(data['start_date'] <= dt) & (data['end_date'] >= dt)][str(WYT)]) / 35.314666

        # Calculate supp IFR
        data_supp = self.read_csv(path + 'IFR_Below Sand Bar Diversion (Supp)_cfs_daily.csv',
                                  names=['Day_st', 'Day_end', '1', '2', '3', '4', '5'], header=0, index_col=None)
        if self.mode == 'scheduling':
            if timestep.month == 10 and timestep.day == 1:
                peak_inflow_Donnells = self.read_csv('Scenarios/Livneh/preprocessed/peak_runoff_DonnellsRes_MarToMay_cms.csv',
                                                     usecols=[0, 1], index_col=[0], parse_dates=[1],
                                                     squeeze=True)  # cms
                self.peak_dt = peak_inflow_Donnells[timestep.year + 1]
            diff_day = (timestep.datetime - self.peak_dt).days
            ifr_supp = 0
            if diff_day > 0 and diff_day <= 91:
                ifr_supp = (data_supp[(data_supp['Day_st'] < diff_day) & (diff_day <= data_supp['Day_end'])][str(WYT)]).values[-1] / 35.314666
            return ifr_val + ifr_supp
        else:
            if timestep.month == 5:
                ifr_supp = data_supp[str(WYT)].loc[0:4].mean()
            elif timestep.month == 6:
                ifr_supp = data_supp[str(WYT)].loc[5:8].mean()
            elif timestep.month == 7:
                ifr_supp = data_supp[str(WYT)].loc[8:12].mean()
            else:
                ifr_supp = 0
        return ifr_val + ifr_supp
        
    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Sand_Bar_Div_Requirement.register()
print(" [*] node_IFR_bl_Sand_Bar_Div_Requirement successfully registered")
