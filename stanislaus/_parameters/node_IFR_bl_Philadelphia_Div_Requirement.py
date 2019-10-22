import datetime
from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Philadelphia_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = int(self.get("WYI_SJValley"))
        management = "BAU"
        path = "Management/{mgt}/IFRs/".format(mgt=management)
        if self.mode == 'scheduling':
            fName = 'IFR_Below Philadelphia Div. (MIF)_cfs_daily.csv'
        else:
            fName = 'IFR_Below Philadelphia Div. (MIF)_cfs_monthly.csv'
        if timestep.datetime.month >= 10:
            dt = datetime.date(1999, timestep.month, timestep.day)
        else:
            dt = datetime.date(2000, timestep.month, timestep.day)

        data = self.read_csv(path + fName, usecols=[0, 1, 2, 3, 4, 5, 6], index_col=None, header=0,
                             names=['start_date', 'end_date', '1', '2', '3', '4', '5'], parse_dates=[0, 1])
        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        ifr_val = (data[(data['start_date'] <= dt) & (data['end_date'] >= dt)][str(WYT)]) / 35.314666
        if self.mode == 'planning':
            ifr_val *= self.days_in_planning_month(timestep, self.month_offset)
        return ifr_val
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Philadelphia_Div_Requirement.register()
print(" [*] node_IFR_bl_Philadelphia_Div_Requirement successfully registered")
