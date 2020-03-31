import numpy as np
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type(WaterLPParameter):
    """"""

    WYT = None

    def setup(self):
        super().setup()
        # allocate an array to hold the previous storage; will be overwritten each timestep
        num_scenarios = len(self.model.scenarios.combinations)
        self.WYT = np.empty(num_scenarios, np.float64)

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        # initial IFR
        if timestep.index == 0:
            self.WYT[sid] = 2  # default

        date = self.datetime

        # These are monthly values, so only calculate values in the first time step of each month
        if date.month >= 9:
            WYT = self.WYT[sid]

        # Jan-June:
        else:
            schedule = self.model.tables["IFR bl Hetch Hetchy Reservoir/IFR Schedule"]

            lookup_row = timestep.month - 1
            if (date.month, date.day) > (9, 15):
                lookup_row += 1

            criteria = (schedule.iat[lookup_row, 1], schedule.iat[lookup_row, 3])

            oct_1 = '{:04}-10-01'.format(date.year - 1)

            if date.month <= 6:
                precip = self.model.parameters["Hetch Hetchy Reservoir/Precipitation"].dataframe
                total_precip = precip[oct_1:date].sum() / 25.4  # sum & convert mm to inches
                if total_precip >= criteria[0]:
                    WYT = 3
                elif total_precip >= criteria[1]:
                    WYT = 2
                else:
                    WYT = 1

            # July-Aug:
            else:
                runoff = self.model.parameters["Hetch Hetchy Reservoir Inflow/Runoff"].dataframe
                cumulative_runoff = runoff[oct_1:date].sum()
                cumulative_runoff *= 810.7 / 1000  # convert mcm to taf
                if cumulative_runoff >= criteria[0]:
                    WYT = 3
                elif cumulative_runoff >= criteria[1]:
                    WYT = 2
                else:
                    WYT = 1

        self.WYT[sid] = WYT

        return WYT

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


IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type.register()
print(" [*] IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type successfully registered")
