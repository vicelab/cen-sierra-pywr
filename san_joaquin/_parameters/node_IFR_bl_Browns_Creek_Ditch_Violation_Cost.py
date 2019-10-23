from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Browns_Creek_Ditch_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return self.model.nodes['Bass Lake'].cost.value(timestep, scenario_index)*1.2
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Browns_Creek_Ditch_Violation_Cost.register()
print(" [*] node_IFR_bl_Browns_Creek_Ditch_Violation_Cost successfully registered")
