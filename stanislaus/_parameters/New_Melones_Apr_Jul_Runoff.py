import pandas as pd
import numpy as np
from parameters import WaterLPParameter


class New_Melones_Apr_Jul_Runoff(WaterLPParameter):
    """"""

    def setup(self):
        super.setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.apr_jul_runoff = np.ones([num_scenarios], np.float) * 350000  # acre-feet

    def _value(self, timestep, scenario_index):
        month = self.datetime.month
        day = self.datetime.day

        if month == 4 and day == 1 or self.model.mode == 'planning' and month in [4, 5, 6, 7]:
            start = '{:04}-04-01'.format(self.datetime.year)
            end = '{:04}-07-31'.format(self.datetime.year)
            self.apr_jul_runoff[scenario_index.global_id] = self.model.tables["Full Natural Flow"][start:end].sum() / 1.2335 * 1000

        return self.apr_jul_runoff[scenario_index.global_id]

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Apr_Jul_Runoff.register()
print(" [*] New_Melones_Apr_Jul successfully registered")
