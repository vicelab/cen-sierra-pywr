import math
from parameters import WaterLPParameter


class node_Lyons_Reservoir_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        x = self.model.parameters['storageValueConstant'].value(timestep, scenario_index)
        beta = self.model.parameters['storage_value_numerator'].value(timestep, scenario_index)
        alpha = self.model.parameters['storage_value_leading'].value(timestep, scenario_index)

        elev = self.model.parameters[self.elevation_param].value(timestep, scenario_index)
        val = alpha * math.exp(x * (beta / elev))
        return val

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Lyons_Reservoir_Storage_Value.register()
print(" [*] node_Lyons_Reservoir_Storage_Value successfully registered")
