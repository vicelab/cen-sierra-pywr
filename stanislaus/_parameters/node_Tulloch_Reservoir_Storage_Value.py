import math
import pandas as pd
import numpy as np
from parameters import WaterLPParameter
from datetime import datetime, timedelta


class node_Tulloch_Reservoir_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        multiplier = self.model.parameters['storageValueConstant'].value(timestep, scenario_index)
        return -0.003 * math.exp(multiplier * (254 / self.model.parameters["node/Lake McClure/Elevation"].value(timestep, scenario_index)))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Tulloch_Reservoir_Storage_Value.register()
print(" [*] node_Tulloch_Reservoir_Storage_Value successfully registered")
