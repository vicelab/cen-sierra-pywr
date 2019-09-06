from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Manzanita_Div_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return self.model.nodes['San Joaquin 2 PH [node]'].base_cost*1.2
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Manzanita_Div_Violation_Cost.register()
print(" [*] node_IFR_bl_Manzanita_Div_Violation_Cost successfully registered")
