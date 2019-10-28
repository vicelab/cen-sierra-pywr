from parameters import WaterLPParameter

from utilities.converter import convert

class Hetch_Hetchy_Reservoir_Storage_Capacity(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return 360.4 * 1000 / 810.7
        
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
        
Hetch_Hetchy_Reservoir_Storage_Capacity.register()
print(" [*] Hetch_Hetchy_Reservoir_Storage_Capacity successfully registered")
