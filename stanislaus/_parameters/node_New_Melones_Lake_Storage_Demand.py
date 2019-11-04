from parameters import WaterLPParameter

from utilities.converter import convert

class node_New_Melones_Lake_Storage_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        flood_control_req = self.read_csv("Management/BAU/LakeMelones_FloodControl_Requirement.csv", index_col=[0],
                                        parse_dates=True, squeeze=True)
        day = timestep.day if timestep.month != 2 else min(timestep.day, 28)
        control_curve_target = flood_control_req['1900-{:02}-{:02}'.format(timestep.month, day)]
        max_storage = self.model.nodes["New Melones Lake"].max_volume
        storage_demand = control_curve_target / max_storage
        return storage_demand

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_New_Melones_Lake_Storage_Demand.register()
print(" [*] node_New_Melones_Lake_Storage_Demand successfully registered")
