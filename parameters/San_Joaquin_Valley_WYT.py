from parameters import WaterLPParameter

from utilities.converter import convert


class San_Joaquin_Valley_WYT(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        SJVI = self.get("San Joaquin Valley WYI" + self.month_suffix, **kwargs)
        thresholds = [0, 2.1, 2.8, 3.1, 3.8]
        WYT = len([x for x in thresholds if SJVI > x])
        return WYT

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


San_Joaquin_Valley_WYT.register()
print(" [*] San_Joaquin_Valley_WYT successfully registered")
