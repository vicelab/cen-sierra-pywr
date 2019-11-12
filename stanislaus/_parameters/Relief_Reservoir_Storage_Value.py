import math
import pandas as pd
import numpy as np
from parameters import WaterLPParameter
from datetime import datetime, timedelta


class Relief_Reservoir_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        if timestep.month >= 11 or timestep.month <= 7:
            return -3500
        else:
            return -60

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


Relief_Reservoir_Storage_Value.register()
print(" [*] Relief_Reservoir_Storage_Value successfully registered")
