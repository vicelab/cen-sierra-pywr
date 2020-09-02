from pywr.parameters import DataFrameParameter


class InflowDataframe(DataFrameParameter):
    bias_correction_factor = False
    bias_correct = False

    def setup(self):
        super().setup()
        if "Bias Correction Factors" in self.model.tables:
            factors = self.model.tables["Bias Correction Factors"]
            if self.name in factors:
                self.bias_correct = True
                self.bias_correction_factor = factors[self.name]

    def value(self, timestep, scenario_index):
        value = super().value(timestep, scenario_index)

        if self.bias_correct:
            value *= self.bias_correction_factor[timestep.month]
            # this could be revised to be either daily or a single value; the table would need to be revised accordingly

        return value


InflowDataframe.register()
