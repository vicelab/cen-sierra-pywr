from parameters import WaterLPParameter

from utilities.converter import convert

class Kerckhoff_Lake_Observed_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        path="Gages/Reservoirs/DailyReservoirGauges.csv"
        return self.read_csv(path)["Kerckhoff Lake"][timestep.datetime]
        
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
        
Kerckhoff_Lake_Observed_Storage.register()
print(" [*] Kerckhoff_Lake_Observed_Storage successfully registered")
