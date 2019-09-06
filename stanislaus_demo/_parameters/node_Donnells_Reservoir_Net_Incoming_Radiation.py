from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_Reservoir_Net_Incoming_Radiation(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        x = 0
        return x
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Donnells_Reservoir_Net_Incoming_Radiation.register()
print(" [*] node_Donnells_Reservoir_Net_Incoming_Radiation successfully registered")
