from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Don_Pedro_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        SJVI = self.get("IFR bl Don Pedro Reservoir/Water Year Type", **kwargs)
        schedule = self.model.parameters["IFR bl Don Pedro Reservoir/IFR Schedule"].array()
        thresholds = [1500, 2000, 2200, 2400, 2700, 3100]
        col = 1 + sum([1 for t in thresholds if SJVI >= t])
        
        if timestep.month == 10 and timestep.day == 20:
            IFR = (schedule[1][col] + schedule[2][col]) / 2
        else:
            if timestep.month == 10 and timestep.day < 15:
                row = 1
            elif timestep.month >= 10 or timestep.month <= 5:
                row = 2
            else:
                row = 3
            IFR = schedule[row][col]
        
        pulse_flow = 0
        if timestep.month == 4 and timestep.day == 30:
            pulse_flow = 700
        elif timestep.month == 4 and timestep.day == 20 or timestep.month == 5 and timestep.day == 10:
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
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Don_Pedro_Reservoir_Requirement.register()
print(" [*] IFR_bl_Don_Pedro_Reservoir_Requirement successfully registered")
