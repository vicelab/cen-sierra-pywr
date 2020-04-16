from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_at_La_Grange_Water_Year_Type(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # San Joaquin Valley Index
        return self.model.parameters["San Joaquin Valley WYI"].get_value(scenario_index)

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_at_La_Grange_Water_Year_Type.register()
