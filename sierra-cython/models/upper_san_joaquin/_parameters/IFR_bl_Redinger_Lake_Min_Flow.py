from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Redinger_Lake_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        year_type = self.model.parameters["San Joaquin Valley WYT" + self.month_suffix].value(timestep, scenario_index)

        # Note: no factor of safety release is assumed
        if year_type <= 2 and timestep.month >= 10 or (timestep.month, timestep.day) <= (4, 1):
            ifr_cfs = 15
        else:
            ifr_cfs = 20

        ifr_cfs = 32  # This overrides the above based on observations post-2006

        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month

        return ifr_cfs / 35.31

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Redinger_Lake_Min_Flow.register()
