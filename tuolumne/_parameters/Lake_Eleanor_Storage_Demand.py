from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_Eleanor_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # min({22: 0.0, 39: 1.0, 40: 0.0}.get(period, 0)*self.get("Lake Eleanor/Storage Capacity", **kwargs), self.get("node/92017/65", **kwargs))
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
        
Lake_Eleanor_Storage_Demand.register()
print(" [*] Lake_Eleanor_Storage_Demand successfully registered")
