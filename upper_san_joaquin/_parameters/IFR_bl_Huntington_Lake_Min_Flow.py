from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_bl_Huntington_Lake_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        ifr_cfs = 2  # TODO: find out what the actual practice is for this IFR. No IFR in winter doesn't make sense.

        if (4, 15) <= (self.datetime.month, self.datetime.day) <= (12, 15):
            ifr_cfs = 2

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


IFR_bl_Huntington_Lake_Min_Flow.register()
