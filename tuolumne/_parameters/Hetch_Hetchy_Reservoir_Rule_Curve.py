from parameters import WaterLPParameter

from utilities.converter import convert

class Preferred_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        preferred_storage_af = self.model.tables["Preferred Storage"].at[(timestep.month, timestep.day), self.res_name]
        max_storage_af = self.model.nodes[self.res_name].max_volume * 1e6 / 1233.5
        preferred_storage_percent = preferred_storage_af / max_storage_af
        return preferred_storage_percent
        
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
        
Preferred_Storage.register()
print(" [*] Preferred_Storage successfully registered")
