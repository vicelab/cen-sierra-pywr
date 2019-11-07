import math
import pandas as pd
import numpy as np
from parameters import WaterLPParameter
from datetime import datetime, timedelta


class node_New_Melones_Reservoir_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        multiplier = self.model.parameters['melones_storageValueConstant'].value(timestep, scenario_index)
        storage_value_numerator = self.model.parameters['melones_storage_value_numerator'].value(timestep, scenario_index)
        leading_multiplier = self.model.parameters['melones_storage_value_leading'].value(timestep, scenario_index)
        # return leading_multiplier * math.exp(multiplier * (storage_value_numerator / self.model.parameters["New Melones Reservoir/Elevation"].value(timestep, scenario_index)))
        return 1

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


node_New_Melones_Reservoir_Storage_Value.register()
print(" [*] node_New_Melones_Reservoir_Storage_Value successfully registered")
