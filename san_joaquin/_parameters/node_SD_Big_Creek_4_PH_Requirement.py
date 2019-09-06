from parameters import WaterLPParameter

from utilities.converter import convert

class node_SD_Big_Creek_4_PH_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return self.model.parameters['node/Big Creek 4 PH/Turbine Capacity'].value(timestep, scenario_index)
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_SD_Big_Creek_4_PH_Requirement.register()
print(" [*] node_SD_Big_Creek_4_PH_Requirement successfully registered")
