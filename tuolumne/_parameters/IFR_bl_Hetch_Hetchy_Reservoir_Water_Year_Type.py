from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # get cumulative precip
        if date.month >= 10:
            start_year = date.year
        else:
            start_year = date.year - 1
        start = '{}-10-10'.format(start_year)
        
        # get criteria
        schedule = self.get("IFR bl Hetch Hetchy Reservoir/IFR Schedule", **kwargs)
        row = date.month + 1
        criteria = [schedule[row][1], schedule[row][3]]
        
        # iniitial IFR
        if date == self.dates[0]:
            WYT = 2 # default
        
        # These are monthly values, so only calculate values in the first time step of each month
        elif date.day > 10 or date.month in [9,10,11,12]:
            WYT = self.get("IFR bl Hetch Hetchy Reservoir/Water Year Type", offset=-1, **kwargs)
        
        # Jan-June:
        elif date.month in [1,2,3,4,5,6]:
            cumulative_precip = get("node/HETCH_HETCHY_RES/Precipitation", \
                                    start=start, agg='sum')
            if cumulative_precip >= criteria[0]:
                WYT = 3
            elif cumulative_precip >= criteria[1]:
                WYT = 2
            else:
                WYT = 1
                
        # July-Aug:
        elif date.month in [7,8]:
            timesteps_to_date = timestep % 36 + 1
            average_cfs = get("node/HETCH_HETCHY_WATERSHED/Runoff", \
                              start=start, agg='mean')
            cumulative_af = average_cfs * 60*60*24*10*timesteps_to_date / 43559.9 / 1000
            
            if cumulative_af >= criteria[0]:
                WYT = 3
            elif cumulative_af >= criteria[1]:
                WYT = 2
            else:
                WYT = 1
            
        return WYT
        
    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type.register()
print(" [*] IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type successfully registered")
