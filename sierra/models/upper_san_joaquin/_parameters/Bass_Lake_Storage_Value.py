from sierra.base_parameters import BaseParameter


class Bass_Lake_Storage_Value(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        x = self.model.tables['San Joaquin Valley Index'][self.operational_water_year]
        y = -15.5
        if x <= 2:
            return y * 3.35
        else:
            return y

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


Bass_Lake_Storage_Value.register()
