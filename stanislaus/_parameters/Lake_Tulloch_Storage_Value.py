from parameters import WaterLPParameter

from utilities.converter import convert
import pandas as pd


class Lake_Tulloch_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        if (4, 1) <= (self.datetime.month, self.datetime.day) <= (9, 15):
            cost = -100.0  # refill period
        else:
            cost = 4000.0  # drawdown period
        return cost

    def value(self, *args, **kwargs):
        try:
            ifr = self.get_ifr(*args, **kwargs)
            if ifr is not None:
                return ifr
            else:
                ifr = self._value(*args, **kwargs)
                return convert(ifr, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_Tulloch_Storage_Value.register()
print(" [*] Lake_Tulloch_Storage_Value successfully registered")
