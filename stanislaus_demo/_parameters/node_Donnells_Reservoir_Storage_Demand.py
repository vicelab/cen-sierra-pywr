from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_Reservoir_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        return 0
        # kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # capacity = self.model.nodes['Donnells Reservoir [node]'].max_volume
        # return min({14: 0.0, 35: 1.0, 36: 0.0}.get(period, 0)*capacity, self.GET("node/91784/65", **kwargs))
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Donnells_Reservoir_Storage_Demand.register()
print(" [*] node_Donnells_Reservoir_Storage_Demand successfully registered")
