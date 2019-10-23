import datetime
from parameters import WaterLPParameter
from utilities.converter import convert

class node_IFR_bl_McKays_Point_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        flw_catchment6 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb06.csv", squeeze=True)[timestep.datetime] #cms
        flw_catchment7 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb07.csv", squeeze=True)[timestep.datetime] #cms
        flw_catchment8 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb08.csv", squeeze=True)[timestep.datetime]  # cms
        flw_catchments = flw_catchment6 + flw_catchment7 + flw_catchment8
        ifr_bl_utica = 0.14158 #cms (5 cfs)
        ifr_bl_NSM = 0.4672 #cms 16.5 cfs
        ifr_val = min(0.4672, flw_catchments + ifr_bl_utica + ifr_bl_NSM)
        if self.mode == 'planning':
            ifr_val *= self.days_in_month()
        return ifr_val

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_IFR_bl_McKays_Point_Div_Requirement.register()
print(" [*] node_IFR_bl_McKays_Point_Div_Requirement successfully registered")
