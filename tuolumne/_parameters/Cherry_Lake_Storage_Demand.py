from parameters import WaterLPParameter

from utilities.converter import convert

class Cherry_Lake_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # min({22: 0.0, 39: 1.0, 40: 0.0}.get(period, 0)*self.get("Cherry Lake/Storage Capacity", **kwargs), self.get("node/92018/65", **kwargs))
        return 0
        
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
        
Cherry_Lake_Storage_Demand.register()
print(" [*] Cherry_Lake_Storage_Demand successfully registered")
