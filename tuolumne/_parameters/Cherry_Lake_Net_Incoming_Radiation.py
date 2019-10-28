from parameters import WaterLPParameter

from utilities.converter import convert

class Cherry_Lake_Net_Incoming_Radiation(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        x = 0
        return x
        
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
        
Cherry_Lake_Net_Incoming_Radiation.register()
print(" [*] Cherry_Lake_Net_Incoming_Radiation successfully registered")
