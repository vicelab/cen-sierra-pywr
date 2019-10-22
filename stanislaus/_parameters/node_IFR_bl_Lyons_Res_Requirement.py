import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_Lyons_Res_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT = int(self.get("WYI_SJValley"))
        flw_catchment22 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb22.csv", squeeze=True)[
            timestep.datetime]  # cms
        flw_catchment23 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb23.csv", squeeze=True)[
            timestep.datetime]  # cms
        flw_catchment24 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb24.csv", squeeze=True)[
            timestep.datetime]  # cms
        flw_catchment25 = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sb25.csv", squeeze=True)[
            timestep.datetime]  # cms
        inflow_res = flw_catchment22 + flw_catchment23 + flw_catchment24 + flw_catchment22
        if timestep.datetime.month >= 10:
            dt = datetime.date(1999, timestep.month, timestep.day)
        else:
            dt = datetime.date(2000, timestep.month, timestep.day)

        if (WYT == 1):
            sch_flow = 5 #cfs
        else:
            if ((datetime.date(1999,10,1) <= dt) & (datetime.date(1999,10,31) >= dt)):
                sch_flow = 8 #cfs
            elif ((datetime.date(1999,11,1) <= dt) & (datetime.date(2000,6,30) >= dt)):
                sch_flow = 10 #cfs
            elif ((datetime.date(2000,7,1) <= dt) & (datetime.date(2000,7,31) >= dt)):
                sch_flow = 8 #cfs
            elif ((datetime.date(1999,8,1) <= dt & datetime.date(2000,9,30) >= dt)):
                sch_flow = 5 #cfs
        ifr_val = min(inflow_res,sch_flow/35.314666)
        if self.mode == 'planning':
            ifr_val *= self.days_in_planning_month(timestep, self.month_offset)
        return ifr_val

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_IFR_bl_Lyons_Res_Requirement.register()
print(" [*] node_IFR_bl_Lyons_Res_Requirement successfully registered")
