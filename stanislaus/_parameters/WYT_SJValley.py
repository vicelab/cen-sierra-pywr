from parameters import WaterLPParameter

from utilities.converter import convert

class WYT_SJValley(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        SJVI = self.GET("WYI_SJValley", **kwargs)
        if SJVI  <=  2.1:
            x = 1
        elif SJVI <= 2.8:
            x = 2
        elif SJVI <= 3.1:
            x = 3
        elif SJVI  <=  3.8:
            x = 4
        else:
            x = 5
        return x
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
WYT_SJValley.register()
print(" [*] WYT_SJValley successfully registered")
