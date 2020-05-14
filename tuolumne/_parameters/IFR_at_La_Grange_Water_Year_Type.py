from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_at_La_Grange_Water_Year_Type(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # San Joaquin Valley Index
        return self.model.parameters["San Joaquin Valley WYI"].get_value(scenario_index)

    def value(self, *args, **kwargs):
        try:
            ifr = self.get_ifr(*args, **kwargs)
            if ifr is not None:
                return ifr
            else:
                ifr = self._value(*args, **kwargs)
                return ifr # unit is already mcm
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_at_La_Grange_Water_Year_Type.register()
