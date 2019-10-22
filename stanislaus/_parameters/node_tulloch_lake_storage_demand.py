from parameters import WaterLPParameter

from utilities.converter import convert
import pandas as pd


class node_Tulloch_Lake_Storage_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        flood_control_req = self.read_csv("Management/BAU/LakeTulloch_FloodControl_Requirement.csv", index_col=[0], parse_dates=True, squeeze=True)
        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        return flood_control_req['1900-{:02}-{:02}'.format(timestep.month, day)]

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Tulloch_Lake_Storage_Demand.register()
print(" [*] node_Tulloch_Lake_Storage_Demand successfully registered")
