from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_bl_Cherry_Lake_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.datetime.month in [7, 8, 9]:
            ifr = 15.5  # cfs
        else:
            ifr = 6  # 5 + 1 as a factor of safety
        return ifr / 35.31

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


IFR_bl_Cherry_Lake_Min_Flow.register()
