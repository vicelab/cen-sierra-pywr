from parameters import WaterLPParameter

from utilities.converter import convert

class Don_Pedro_Reservoir_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        #water_bank_maximum_storage = 570 # TAF
        
        targets = [1690,1690,1690,1717.6,2002.4,2030,2030,2030,1773,1690,1690,1690]
        #return [1070, targets[date.month - 1] - 570]
        return targets[date.month - 1] # TAF
        
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
        
Don_Pedro_Reservoir_Storage_Demand.register()
print(" [*] Don_Pedro_Reservoir_Storage_Demand successfully registered")
