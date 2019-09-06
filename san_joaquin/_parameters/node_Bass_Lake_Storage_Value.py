from parameters import WaterLPParameter

from utilities.converter import convert

class node_Bass_Lake_Storage_Value(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        x=self.get("WYT_SJValley", **kwargs)
        y=15.5
        if x<=2:
            return -y*3.35
        else:
            return -y
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Bass_Lake_Storage_Value.register()
print(" [*] node_Bass_Lake_Storage_Value successfully registered")
