from pywr.parameters import Parameter


class Planning_Initial_Storage(Parameter):
    """"""

    def __init__(self, model, reservoir, **kwargs):
        super().__init__(model, **kwargs)
        self.reservoir = reservoir

    def _value(self, timestep, scenario_index):

        initial_storage = self.model.scheduling.nodes[self.reservoir].volume[scenario_index.global_id]
        return initial_storage

    def value(self, *args, **kwargs):
        try:
            return self._value(*args, **kwargs)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        reservoir = data.pop('reservoir')
        return cls(model, reservoir, **data)


Planning_Initial_Storage.register()
