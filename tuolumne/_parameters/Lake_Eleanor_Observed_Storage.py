from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_Eleanor_Observed_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        df = self.read_csv("Observed/Reservoirs/GaugeReservoir_mcm_TUO_R3.csv", index_col=0, header=0)
        return df["Lake Eleanor Reservoir"][timestep.datetime]
        
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
        
Lake_Eleanor_Observed_Storage.register()
print(" [*] Lake_Eleanor_Observed_Storage successfully registered")
