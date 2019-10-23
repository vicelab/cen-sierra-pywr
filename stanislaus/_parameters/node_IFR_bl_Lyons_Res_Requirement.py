import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_Lyons_Res_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.get("WYT_SJValley")

        # ifr is in cfs
        if WYT == 1:
            ifr = 5
        else:
            month = timestep.month  # not necessary, but a little easier to read
            if month == 10:  # Oct
                ifr = 8
            elif month >= 11 or month <= 6:  # Nov-Jun
                ifr = 10
            elif month == 7:  # July
                ifr = 8
            else:  # Aug-Sep
                ifr = 5
        ifr *= self.cfs_to_cms
        if self.mode == 'planning':
            ifr *= self.days_in_month()
        return ifr

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_IFR_bl_Lyons_Res_Requirement.register()
print(" [*] node_IFR_bl_Lyons_Res_Requirement successfully registered")
