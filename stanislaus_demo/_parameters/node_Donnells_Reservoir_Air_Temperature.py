from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_Reservoir_Air_Temperature(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        path="{ExternalDir}/{Scenario}/Climate/STN_18_Temperature.csv".format(ExternalDir=self.GET("network/1235/1594", **kwargs), Scenario=self.GET("network/1235/1595", **kwargs))
        data = self.read_csv(path, usecols=[0,1,2], comment=';', header=None, **kwargs)
        return data.iloc[timestep][2]
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Donnells_Reservoir_Air_Temperature.register()
print(" [*] node_Donnells_Reservoir_Air_Temperature successfully registered")
