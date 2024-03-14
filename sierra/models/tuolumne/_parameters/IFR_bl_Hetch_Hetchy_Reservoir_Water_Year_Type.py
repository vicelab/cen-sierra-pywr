import numpy as np
from sierra.base_parameters import MinFlowParameter

class IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type(MinFlowParameter):
    def setup(self):
        super().setup()
        # Allocate an array to hold the previous storage; will be overwritten each timestep
        num_scenarios = len(self.model.scenarios.combinations)
        self.WYT = np.empty(num_scenarios, np.float64)

    def _value(self, timestep, scenario_index):
        sid = scenario_index.global_id
        # Initial IFR
        if timestep.index == 0:
            self.WYT[sid] = 2  # Default

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
                total_precip = precip[oct_1:date].sum() / 25.4  # Sum & convert mm to inches
                if total_precip < 6.1:
                    WYT = 1
                elif 6.1 <= total_precip < 8.8:
                    WYT = 2
                else:
                    WYT = 3

            # July-Aug:
            else:
                runoff = self.model.parameters["Hetch Hetchy Reservoir Inflow/Runoff"].dataframe
                cumulative_runoff = runoff[oct_1:date].sum()
                cumulative_runoff *= 810.7 / 1000  # Convert mcm to taf
                if cumulative_runoff < 390:
                    WYT = 1
                elif 390 <= cumulative_runoff < 575:
                    WYT = 2
                else:
                    WYT = 3

        self.WYT[sid] = WYT

        return WYT

    def value(self, *args, **kwargs):
        return self._value(*args, **kwargs)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type.register()
