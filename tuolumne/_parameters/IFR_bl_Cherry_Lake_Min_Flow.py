from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Cherry_Lake_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.datetime.month in [7, 8, 9]:
            ifr = 15.5  # cfs
        else:
            ifr = 6  # 5 + 1 as a factor of safety
        return ifr / 35.31

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
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


IFR_bl_Cherry_Lake_Min_Flow.register()
