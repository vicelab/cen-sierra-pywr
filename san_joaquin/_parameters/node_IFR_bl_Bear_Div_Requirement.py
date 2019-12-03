from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Bear_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        year_type = self.model.parameters["WYT_SJValley"].values(timestep, scenario_index)
        month = self.datetime.month
        return_val = 0

        if year_type in [1, 2]:  # Critical or Dry WYT
            if month in [5,6,7,8,9]:
                return_val = 2
            else:
                return_val = 1
        else:
            if month in [5,6,7,8,9]:
                return_val = 3
            else:
                return_val = 2

        if self.model.mode == "planning":
            return_val *= self.days_in_month()

        return return_val
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Bear_Div_Requirement.register()
print(" [*] node_IFR_bl_Bear_Div_Requirement successfully registered")
