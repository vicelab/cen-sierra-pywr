import pandas as pd
from parameters import WaterLPParameter


class New_Melones_Apr_Jul_Runoff(WaterLPParameter):
    """"""

    apr_jul_runoff = 350000  # acre-feet

    def _value(self, timestep, scenario_index):
        month = self.datetime.month
        day = self.datetime.day
        mode = self.model.mode
        if month == 4 and day == 1 or mode == 'planning' and month in [4, 5, 6, 7]:

            start = '{:04}-04-01'.format(self.datetime.year)
            end = '{:04}-07-31'.format(self.datetime.year)
            total_runoff = 0
            for j in range(1, 26):
                if self.model.mode == 'scheduling':
                    runoff = self.model.parameters['STN_{:02} Headflow/Runoff'.format(j)].dataframe[start:end].sum()
                else:
                    runoff = self.model.parameters['STN_{:02} Headflow/Runoff/1'.format(j)].dataframe[start:end].sum()
                total_runoff += runoff / 1.2335 * 1000  # mcm to af
            self.apr_jul_runoff = total_runoff

        return self.apr_jul_runoff

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
