from pywr.parameters import DataFrameParameter
from parameters import WaterLPParameter
from datetime import datetime, timedelta
from scipy import interpolate
import numpy as np
from utilities.converter import convert


class Dataframe2(DataFrameParameter):

    bias_correction_factor = False

    def __init__(self, *args, **kwargs):
        self.bias_correct = kwargs.pop('bias_correct', False)
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()
        bias_correct = False
        if self.bias_correct and "Bias Correction Factors" in self.model.tables:
            factors = self.model.tables["Bias Correction Factors"]
            if self.name in factors:
                bias_correct = True
                self.bias_correction_factor = factors[self.name]
        self.bias_correct = bias_correct

    def value(self, timestep, scenario_index):
        value = super().value(timestep, scenario_index)

        if self.bias_correct:
            value *= self.bias_correction_factor[timestep.month]
            # this could be revised to be either daily or a single value; the table would need to be revised accordingly

        return value

    # @classmethod
    # def load(cls, model, data):
    #     type = data.pop('type', None)
    #     return cls(type, model, data)


Dataframe2.register()
