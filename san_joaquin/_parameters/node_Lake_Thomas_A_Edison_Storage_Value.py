from parameters import WaterLPParameter

from utilities.converter import convert

class node_Lake_Thomas_A_Edison_Storage_Value(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return 90
        x=self.get("WYT_SJValley", **kwargs)
        if x <=2:
            return -77
        else:
            return -80.8
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Lake_Thomas_A_Edison_Storage_Value.register()
print(" [*] node_Lake_Thomas_A_Edison_Storage_Value successfully registered")
