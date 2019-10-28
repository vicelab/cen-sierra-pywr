from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Don_Pedro_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        SJVI = self.GET("IFR bl Don Pedro Reservoir/Water Year Type", **kwargs)
        schedule = self.GET("IFR bl Don Pedro Reservoir/IFR Schedule", **kwargs)
        thresholds = [1500, 2000, 2200, 2400, 2700, 3100]
        col = 1
        for threshold in thresholds:
            if SJVI < threshold:
                break
            col += 1
        
        if date.month == 10 and date.day == 20:
            IFR = (schedule[1][col] + schedule[2][col]) / 2
        else:
            if date.month == 10 and date.day < 15:
                row = 1
            elif date.month >= 10 or date.month <= 5:
                row = 2
            else:
                row = 3
            IFR = schedule[row][col]
        
        pulse_flow = 0
        if date.month == 4 and date.day == 30:
            pulse_flow = 700
        elif date.month == 4 and date.day == 20 or date.month == 5 and date.day == 10:
            pulse_flow = 350
            
        return max(IFR, pulse_flow, 100)
        
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
        return cls(model, **data)
        
IFR_bl_Don_Pedro_Reservoir_Requirement.register()
print(" [*] IFR_bl_Don_Pedro_Reservoir_Requirement successfully registered")
