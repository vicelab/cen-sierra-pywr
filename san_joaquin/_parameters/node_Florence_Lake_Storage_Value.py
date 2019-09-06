from parameters import WaterLPParameter

from utilities.converter import convert

class node_Florence_Lake_Storage_Value(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return 85
        x=self.get("WYT_SJValley", **kwargs)
        if self.get("node/Florence Lake/Drawdown", **kwargs) == 1:
            y=10
        else:
            y=78
        return -y
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Florence_Lake_Storage_Value.register()
print(" [*] node_Florence_Lake_Storage_Value successfully registered")
