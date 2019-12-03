from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Chinquapin_Creek_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        return_val = 0
        month = self.datetime.month
        if month in [5,6,7,8,9]:
            return_val = 1
        else:
            return_val = 0.5

        if self.model.mode == "planning":
            return_val *= self.days_in_month()
        return return_val
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "cfs", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Chinquapin_Creek_Div_Requirement.register()
print(" [*] node_IFR_bl_Chinquapin_Creek_Div_Requirement successfully registered")
