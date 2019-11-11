from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Big_Creek_6_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        return 3
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "cfs", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Big_Creek_6_Div_Requirement.register()
print(" [*] node_IFR_bl_Big_Creek_6_Div_Requirement successfully registered")
