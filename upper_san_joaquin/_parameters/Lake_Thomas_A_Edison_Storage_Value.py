from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_Thomas_A_Edison_Storage_Value(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return -90
        x=self.get("WYT_SJValley", **kwargs)
        if x <=2:
            return -77
        else:
            return -80.8
        
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
        
Lake_Thomas_A_Edison_Storage_Value.register()
print(" [*] Lake_Thomas_A_Edison_Storage_Value successfully registered")
