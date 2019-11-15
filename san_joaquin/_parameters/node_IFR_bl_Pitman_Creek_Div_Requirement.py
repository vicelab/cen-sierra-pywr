from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Pitman_Creek_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        return_val = convert(0.3, 'ft^3 s^-1', 'hm^3 day^-1')
        if self.model.mode == "planning":
            return_val *= self.days_in_month()
        return return_val
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Pitman_Creek_Div_Requirement.register()
print(" [*] node_IFR_bl_Pitman_Creek_Div_Requirement successfully registered")
