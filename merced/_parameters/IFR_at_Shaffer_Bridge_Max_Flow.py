from parameters import WaterLPParameter
from datetime import date
import numpy as np


class IFR_at_Shaffer_Bridge_Max_Flow(WaterLPParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    def _value(self, timestep, scenario_index):

        ifr_val = 250 / 35.31  # cfs to cms (16.5 cfs)
        ifr_range = self.get_ifr_range(timestep, scenario_index, initial_value=ifr_val, rate=0.25)

        return ifr_range * 0.0864

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)


    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_at_Shaffer_Bridge_Max_Flow.register()
print(" [*] IFR_at_Shaffer_Bridge_Max_Flow successfully registered")
