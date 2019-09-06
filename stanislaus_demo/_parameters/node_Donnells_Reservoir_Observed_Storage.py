from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_Reservoir_Observed_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return self.read_csv('Scenarios/Livneh/res_STNR.csv', squeeze=True)[timestep.datetime]
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Donnells_Reservoir_Observed_Storage.register()
print(" [*] node_Donnells_Reservoir_Observed_Storage successfully registered")
