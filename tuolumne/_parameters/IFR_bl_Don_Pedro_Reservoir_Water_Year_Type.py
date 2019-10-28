from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Don_Pedro_Reservoir_Water_Year_Type(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # San Joaquin Valley Index
        SJVI = [1970, 2060, 2720, 3550, 5580, 2180, 1710, 1160][date.year - 2007]
        
        return SJVI
        
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
        
IFR_bl_Don_Pedro_Reservoir_Water_Year_Type.register()
print(" [*] IFR_bl_Don_Pedro_Reservoir_Water_Year_Type successfully registered")
