from parameters import WaterLPParameter

from utilities.converter import convert
import pandas as pd

flood_control_req = pd.read_csv("s3_imports/LakeMelone_FloodControl_Requirement.csv", index_col=[0])
flood_control_req.index = pd.to_datetime(flood_control_req.index)

class node_New_Melones_Storage_Demand(WaterLPParameter):

    def value(self, timestep, scenario_index):
        timestep_str = str(timestep.datetime).split()[0].split("-")
        timestep_str[0] = "1900"
        timestep_str = "-".join(timestep_str)
        return flood_control_req.loc[timestep_str].values[0]

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_New_Melones_Storage_Demand.register()
print(" [*] node_New_Melones_Storage_Demand successfully registered")
