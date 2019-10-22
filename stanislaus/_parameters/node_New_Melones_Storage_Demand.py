from parameters import WaterLPParameter

from utilities.converter import convert

class node_New_Melones_Storage_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        flood_control_req = self.read_csv("Management/BAU/LakeMelones_FloodControl_Requirement.csv", index_col=[0],
                                        parse_dates=True, squeeze=True)
        day = timestep.day if timestep.month != 2 else min(timestep.day, 28)
        return flood_control_req['1900-{:02}-{:02}'.format(timestep.month, day)]

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_New_Melones_Storage_Demand.register()
print(" [*] node_New_Melones_Storage_Demand successfully registered")
