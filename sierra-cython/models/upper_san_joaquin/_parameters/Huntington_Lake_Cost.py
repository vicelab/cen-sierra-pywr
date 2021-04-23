from sierra.base_parameters import WaterLPParameter


class Huntington_Lake_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        # return 0.0
        if self.model.mode == 'scheduling':
            # cost = -85
            if self.datetime.month in [6, 7, 8]:
                cost = -1000
            else:
                cost = -85
        else:
            # cost = -85
            cost = 0.0
        return cost

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


Huntington_Lake_Cost.register()
