from parameters import WaterLPParameter

from utilities.converter import convert

class Gauge_Moccasin_PH_Observed_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        path="{ExternalDir}/GAGES/Hydropower_flow/SFPUC_MPH_Moccasin_Powerhouse.csv".format(ExternalDir=self.GET("network/1237/1594", **kwargs))
        data = self.read_csv(path, usecols=[0,1,2], comment=';', header=None, **kwargs)
        return data.iloc[timestep][2]*self.GET("network/1237/1584", **kwargs)
        
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
        return cls(model, **data)
        
Gauge_Moccasin_PH_Observed_Flow.register()
print(" [*] Gauge_Moccasin_PH_Observed_Flow successfully registered")
