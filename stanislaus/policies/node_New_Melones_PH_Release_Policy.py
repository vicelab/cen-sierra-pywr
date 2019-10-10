import math
import pandas as pd
import numpy as np
from parameters import WaterLPParameter
from datetime import datetime, timedelta
from utilities.get_year_type import getSJVI_WYT

flow_threshold = 19.572
class New_Melones_Release_Policy(WaterLPParameter):

    def get_demand(self, timestep, scenario_index):
        million_m3day_to_m3sec = 11.5740740741
        year_names = ["Critical", "Dry", "Below", "Above", "Wet"]
        timestep_datetime = timestep.datetime
        timestep_datetime = datetime(1990, timestep_datetime.month, timestep_datetime.day)

        year_type = year_names[getSJVI_WYT(timestep)-1]
        net_demand_csv = self.read_csv("s3_imports/NetDemand_belowTulloch.csv", index_col=[0])

        date = "/".join([str(timestep_datetime.month), str(timestep_datetime.day), str(timestep_datetime.year)])

        return net_demand_csv.loc[date, year_type] / million_m3day_to_m3sec

    def get_itot(self, timestep):
        runoff_sum = self.read_csv("s3_imports/tot_runoff_sum.csv")
        runoff_sum.index = pd.to_datetime(runoff_sum.index)
        runoff_sum = runoff_sum.loc[timestep.datetime:datetime(timestep.year, 7, 31)]

        return runoff_sum.sum()[0]

    def get_dtot(self, timestep, daysaway):
        million_m3day_to_m3sec = 11.5740740741
        date_timestep = datetime(1990, timestep.datetime.month, timestep.datetime.day)
        timestep = timestep.datetime
        year_names = ["Critical", "Dry", "Below", "Above", "Wet"]
        demand_sum = self.read_csv("s3_imports/NetDemand_belowTulloch.csv")
        demand_sum.index = pd.to_datetime(demand_sum.index)
        return_value = 0

        for index in range(0, daysaway):
            year_type = year_names[getSJVI_WYT(timestep) - 1]
            return_value += demand_sum.loc[date_timestep, year_type] / million_m3day_to_m3sec
            date_timestep = date_timestep + timedelta(days=1)
            timestep = timestep + timedelta(days=1)
        return return_value

    def _value(self, timestep, scenario_index):
        date_timestep = datetime(1900, timestep.datetime.month, timestep.datetime.day)
        out_flow = self.model.nodes["New Melones Lake [node]"].volume[-1] + \
                   self.model.nodes["STN_01 Inflow [node]"].flow[-1] - self.model.parameters[
                       "node/New Melones/Storage Demand"].value(timestep, scenario_index)
        net_demand = self.get_demand(timestep, scenario_index) + self.model.parameters["node/blwTullochPH/Requirement"].value(timestep, scenario_index)

        if datetime(1900, 3, 21) < date_timestep < datetime(1900, 5, 31):
            days_till = (datetime(1900, 7, 31) - date_timestep).days
            itot = self.get_itot(timestep)
            dtot = self.get_dtot(timestep, days_till)

            out_flow = (self.model.nodes["New Melones Lake [node]"].max_volume -
                        (self.model.nodes["New Melones Lake [node]"].volume[-1]+itot-dtot))/days_till
            return max(net_demand, min(out_flow, flow_threshold))
        elif datetime(1900, 8, 1) < date_timestep < datetime(1900, 9, 14):
            return net_demand
        else:
            return max(net_demand, min(out_flow, flow_threshold))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Release_Policy.register()
print(" [*] New_Melones_Release_Policy successfully registered")
