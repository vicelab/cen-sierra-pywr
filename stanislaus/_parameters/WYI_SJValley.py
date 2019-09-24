import pandas as pd
from parameters import WaterLPParameter

from utilities.converter import convert

class WYI_SJValley(WaterLPParameter):
    """"""

    def value(self, timestep, scenario_index):
        return pd.read_csv("s3_imports/SJVI.csv", index_col=0, header=0, parse_dates=False,
                           squeeze=True).loc[timestep.year]

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
WYI_SJValley.register()
print(" [*] WYI_SJValley successfully registered")
