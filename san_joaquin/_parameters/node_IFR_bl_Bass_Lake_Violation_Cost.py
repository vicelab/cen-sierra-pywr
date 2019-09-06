from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Bass_Lake_Violation_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # return self.model.parameters['node/San Joaquin 3 PH/Base Value'].value(timestep, scenario_index)*1.2
        return self.model.nodes['San Joaquin 3 PH [node]'].base_cost*1.2

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Bass_Lake_Violation_Cost.register()
print(" [*] node_IFR_bl_Bass_Lake_Violation_Cost successfully registered")
