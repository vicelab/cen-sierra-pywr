from parameters import WaterLPParameter

from utilities.converter import convert

class node_Redinger_Lake_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        # kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # return self.get("node/Redinger Lake/Storage Capacity", **kwargs)
        return self.model.nodes['Redinger Lake'].max_volume
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Redinger_Lake_Storage_Demand.register()
print(" [*] node_Redinger_Lake_Storage_Demand successfully registered")
