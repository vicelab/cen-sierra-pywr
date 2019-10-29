from parameters import WaterLPParameter

from utilities.converter import convert

class WYI_SJValley(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        sjvi = self.read_csv("Scenarios/Livneh/WYT/SJVI.csv", parse_dates=False, squeeze=True)
        water_year = timestep.year if timestep.month < 10 else timestep.year + 1
        return sjvi[water_year]
        
    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "ac-ft", "m^3", scale_in=1000000, scale_out=1000000.0)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
WYI_SJValley.register()
print(" [*] WYI_SJValley successfully registered")
