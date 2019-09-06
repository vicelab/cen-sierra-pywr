from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Kerckhoff_Lake_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        k1 =self.model.nodes['Kerckhoff 1 PH [node]'].base_cost
        k2 =self.model.nodes['Kerckhoff 2 PH [node]'].base_cost
        return max(k1, k2)*1.2
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Kerckhoff_Lake_Violation_Cost.register()
print(" [*] node_IFR_bl_Kerckhoff_Lake_Violation_Cost successfully registered")
