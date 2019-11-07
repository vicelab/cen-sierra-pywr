import math
from parameters import WaterLPParameter


class node_Tulloch_Reservoir_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        multiplier = self.model.parameters['storageValueConstant'].value(timestep, scenario_index)
        elev = self.model.parameters[self.elevation_param].value(timestep, scenario_index)
        val = -0.003 * math.exp(multiplier * (254 / elev))
        return val

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


node_Tulloch_Reservoir_Storage_Value.register()
print(" [*] node_Tulloch_Reservoir_Storage_Value successfully registered")
