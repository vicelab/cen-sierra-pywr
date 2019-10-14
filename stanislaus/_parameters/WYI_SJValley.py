import pandas as pd
from parameters import WaterLPParameter


class WYI_SJValley(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        sjvi = self.read_csv("Scenarios/Livneh/WYT/SJVI.csv", parse_dates=False, squeeze=True)
        water_year = timestep.year if timestep.month < 10 else timestep.year + 1
        return sjvi[water_year]

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


WYI_SJValley.register()
print(" [*] WYI_SJValley successfully registered")
