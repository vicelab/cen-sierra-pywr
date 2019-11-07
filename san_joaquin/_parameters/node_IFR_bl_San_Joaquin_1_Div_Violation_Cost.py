from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_San_Joaquin_1_Div_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        x=self.model.nodes['San Joaquin 1 PH'].base_cost
        y=self.model.nodes['San Joaquin 1A PH'].base_cost
        if (x >= y):
            return x*1.2
        else:
            return y*1.2
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_San_Joaquin_1_Div_Violation_Cost.register()
print(" [*] node_IFR_bl_San_Joaquin_1_Div_Violation_Cost successfully registered")
