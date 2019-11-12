from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Browns_Creek_Ditch_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        month = timestep.datetime.month
        year_type = self.model.parameters["WYT_SJValley"].values(timestep, scenario_index)
        prescribed = 0

        if month == 1:
            prescribed = 4.5
        elif month == 2:
            prescribed = 8
        elif month == 3 or month == 4:
            prescribed = 10
        elif month == 5:
            prescribed = 8
        else:
            prescribed = 4.5

        if year_type in [1,2]:  # Critical or Dry WYT
            return 3
        else:
            return prescribed
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Browns_Creek_Ditch_Requirement.register()
print(" [*] node_IFR_bl_Browns_Creek_Ditch_Requirement successfully registered")
