from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Don_Pedro_Reservoir_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        SJVI = self.get("San Joaquin Valley WYI", timestep, scenario_index)
        schedule_cfs = self.model.tables["IFR bl Don Pedro Reservoir/IFR Schedule"]
        thresholds = [1.500, 2.000, 2.200, 2.400, 2.700, 3.100]
        lookup_col = sum([1 for t in thresholds if SJVI >= t])

        date = self.datetime
        month_day = (self.datetime.month, self.datetime.day)
        if (10, 1) <= month_day <= (10, 15):
            lookup_row = 0
        elif month_day >= (10, 16) or month_day <= (5, 31):
            lookup_row = 1
        else:
            lookup_row = 2

        base_ifr_cfs = schedule_cfs.iat[lookup_row, lookup_col]

        pulse_flow = 0
        if date.month == 4 and date.day > 20:
            pulse_flow = 700 / 10
        elif (4, 20) < month_day <= (5, 10):
            pulse_flow = 350 / 20
            
        ifr_cfs = max(base_ifr_cfs, pulse_flow, 100)
        return ifr_cfs / 35.315
        
    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Don_Pedro_Reservoir_Min_Flow.register()
print(" [*] IFR_bl_Don_Pedro_Reservoir_Min_Flow successfully registered")
