import numpy as np
from sierra.base_parameters import BaseParameter


class New_Melones_Apr_Jul_Runoff(BaseParameter):
    """"""

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.apr_jul_runoff = np.ones(num_scenarios, np.float) * 350000

    def _value(self, timestep, scenario_index):
        month = self.datetime.month
        day = self.datetime.day

        if month == 4 and day == 1 or self.model.mode == 'planning' and month in [4, 5, 6, 7]:
            start = '{:04}-04-01'.format(self.datetime.year)
            end = '{:04}-07-31'.format(self.datetime.year)
            self.apr_jul_runoff[scenario_index.global_id] = self.model.parameters["Full Natural Flow"].dataframe[start:end].sum() / 1.2335 * 1000

        return self.apr_jul_runoff[scenario_index.global_id]

    def value(self, *args, **kwargs):
        val = self._value(*args, **kwargs)
        return val

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Apr_Jul_Runoff.register()
