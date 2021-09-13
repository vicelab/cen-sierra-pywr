from sierra.base_parameters import BaseParameter

from scipy import interpolate


class Lake_McClure_Spill_Max_Flow(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):
        if timestep.index == 0:
            table = self.model.tables["Lake McClure Spill/ESRD"]
            rows = table.iloc[1:, 0]
            cols = table.iloc[0, 1:]
            values = table.values[1:, 1:]
            self.esrd_spline = interpolate.RectBivariateSpline(rows, cols, values, kx=1, ky=1)


        elevation = self.model.parameters["Lake McClure/Elevation"].value(timestep, scenario_index)

        # min release
        # if elevation <= 192.6336:  # 632 ft
        #     release_cms =

        # ESRD
        inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)
        max_cms = self.esrd_spline(elevation, inflow)
        max_mcm = max_cms * 0.0864
        return max_mcm

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_McClure_Spill_Max_Flow.register()
