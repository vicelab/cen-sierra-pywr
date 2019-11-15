from parameters import WaterLPParameter

from utilities.converter import convert
import datetime

class node_IFR_bl_Huntington_Lake_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        return_val = 0
        current_date = self.datetime

        startdate = datetime.date(current_date.year, 4, 15)
        enddate = datetime.date(current_date.year, 12, 15)

        if startdate <= current_date <= enddate:
            return_val = 2

        if self.model.mode == "planning":
            return_val *= self.days_in_month()
        return return_val

        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "cfs", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Huntington_Lake_Requirement.register()
print(" [*] node_IFR_bl_Huntington_Lake_Requirement successfully registered")
