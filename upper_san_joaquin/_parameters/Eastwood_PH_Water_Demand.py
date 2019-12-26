from parameters import WaterLPParameter

from utilities.converter import convert

class Eastwood_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return self.regression_hydropower_demand(timestep, scenario_index, 'HFR_11238250_EastwoodPH', capacity=self.get("node/87405/1615", **kwargs))
        
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
        
Eastwood_PH_Water_Demand.register()
print(" [*] Eastwood_PH_Water_Demand successfully registered")
