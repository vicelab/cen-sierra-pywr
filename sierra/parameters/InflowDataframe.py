from pywr.parameters import DataFrameParameter


class InflowDataframe(DataFrameParameter):
    """
    This parameter type extends the base DataFrameParameter by looking for a bias correction factor table
    in the model. If found, and the name of the parameter is in the table, then it will pull the correction factor
    from the table and multiply the original value by the correction factor.
    """
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
