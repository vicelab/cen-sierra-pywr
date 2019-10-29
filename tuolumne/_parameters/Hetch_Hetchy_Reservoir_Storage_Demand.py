from parameters import WaterLPParameter

from utilities.converter import convert

class Hetch_Hetchy_Reservoir_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # {14: 0.0, 39: 1.0, 40: 0.0}.get(period, 0)*(get("undefined") - get("Inactive Pool"))+get("Inactive Pool")
        return 0
        
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
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
Hetch_Hetchy_Reservoir_Storage_Demand.register()
print(" [*] Hetch_Hetchy_Reservoir_Storage_Demand successfully registered")
