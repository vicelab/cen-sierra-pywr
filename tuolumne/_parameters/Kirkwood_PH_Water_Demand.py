from parameters import WaterLPParameter

from utilities.converter import convert

class Kirkwood_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return 0
        
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
        
Kirkwood_PH_Water_Demand.register()
print(" [*] Kirkwood_PH_Water_Demand successfully registered")
