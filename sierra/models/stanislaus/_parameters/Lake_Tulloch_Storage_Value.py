from sierra.base_parameters import BaseParameter


class Lake_Tulloch_Storage_Value(BaseParameter):

    def _value(self, timestep, scenario_index):
        if (4, 1) <= (self.datetime.month, self.datetime.day) <= (9, 15):
            cost = -100.0  # refill period
        else:
            cost = 4000.0  # drawdown period
        return cost

    def value(self, *args, **kwargs):
        val = self._value(*args, **kwargs)
        return val

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_Tulloch_Storage_Value.register()
