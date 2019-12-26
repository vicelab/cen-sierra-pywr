from parameters import WaterLPParameter

from utilities.converter import convert

class Florence_Lake_Storage_Value(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return 85
        x=self.get("WYT_SJValley", **kwargs)
        if self.get("node/87408/1612", **kwargs) == 1:
            y=10
        else:
            y=78
        return -y
        
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
        
Florence_Lake_Storage_Value.register()
print(" [*] Florence_Lake_Storage_Value successfully registered")
