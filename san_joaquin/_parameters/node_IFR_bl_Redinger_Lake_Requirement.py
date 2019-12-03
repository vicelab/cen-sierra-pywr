from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Redinger_Lake_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        month = self.datetime.month
        year_type = self.model.parameters["WYT_SJValley"].values(timestep, scenario_index)
        return_val = 0

        if month in [10, 11, 12, 1, 2, 3, 4] and year_type in [1,2]: # October - April and Dry or Critical
            return_val = 15
        else:
            return_val = 20

        if self.model.mode == "planning":
            return_val *= self.days_in_month()

        return return_val
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "cfs", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Redinger_Lake_Requirement.register()
print(" [*] node_IFR_bl_Redinger_Lake_Requirement successfully registered")
