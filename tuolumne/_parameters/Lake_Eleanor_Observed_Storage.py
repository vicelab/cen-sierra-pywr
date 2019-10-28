from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_Eleanor_Observed_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        path="{ExternalDir}/GAGES/Reservoirs/USGS_11277500_LK_ELEANOR_NR_HETCH_HETCHY_CA.csv".format(ExternalDir=self.GET("network/1237/1594", **kwargs))
        data = self.read_csv(path, usecols=[0,1,2], comment=';', header=None, **kwargs)
        return data.iloc[timestep][2]*1233/1000000
        
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
        
Lake_Eleanor_Observed_Storage.register()
print(" [*] Lake_Eleanor_Observed_Storage successfully registered")
