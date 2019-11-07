from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Big_Creek_5_Div_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # return self.model.parameters['node/Big Creek 8 PH/Base Value'].value(timestep, scenario_index)*1.2
        return self.model.nodes['Big Creek 8 PH'].base_cost*1.2

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Big_Creek_5_Div_Violation_Cost.register()
print(" [*] node_IFR_bl_Big_Creek_5_Div_Violation_Cost successfully registered")
