from sierra.base_parameters import BaseParameter
from math import exp


class Donnells_Reservoir_Storage_Value(BaseParameter):

    def _value(self, timestep, scenario_index):
        base_cost = -60
        if self.model.mode == 'planning':
            return base_cost
        elev = self.model.nodes[self.res_name].get_level(scenario_index)
        offset = 100

        max_elev = 1498.7
        k = 0.3
        val = min(-exp(k * (max_elev - elev)), -offset) + offset + base_cost
        return val

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Donnells_Reservoir_Storage_Value.register()
