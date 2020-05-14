from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_at_La_Grange_Water_Year_Type(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # San Joaquin Valley Index
        return self.model.parameters["San Joaquin Valley WYI"].get_value(scenario_index)

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


IFR_at_La_Grange_Water_Year_Type.register()
