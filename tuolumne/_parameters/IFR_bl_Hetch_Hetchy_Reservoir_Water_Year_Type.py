from parameters import WaterLPParameter
from datetime import datetime
from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Water_Year_Type(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)

        # initial IFR
        if timestep.index == 0:
            WYT = 2  # default

        # These are monthly values, so only calculate values in the first time step of each month
        elif timestep.month >= 9:
            WYT = self.WYT

        # Jan-June:
        else:
            schedule = self.model.parameters["IFR bl Hetch Hetchy Reservoir/IFR Schedule"].array()
            if timestep.month < 9 or timestep.month == 9 and timestep.day <= 15:
                row = timestep.month + 1
            else:
                row = timestep.month + 2
            criteria = (schedule[row, 2], schedule[row, 4])

            if timestep.month <= 6:
                # precip = self.get("Hetch Hetchy Reservoir/Precipitation").dataframe
                # total_precip = precip[datetime(timestep.year - 1, 10, 1):timestep.datetime].sum()
                total_precip = 1000
                if total_precip >= criteria[0]:
                    WYT = 3
                elif total_precip >= criteria[1]:
                    WYT = 2
                else:
                    WYT = 1

            # July-Aug:
            else:
                runoff = self.get("TUO_13 Headflow/Runoff").dataframe
                cumulative_runoff = runoff[datetime(timestep.year - 1, 10, 1):timestep.datetime].sum()
                cumulative_runoff *= 810.7  # convert mcm to af
                if cumulative_runoff >= criteria[0]:
                    WYT = 3
                elif cumulative_runoff >= criteria[1]:
                    WYT = 2
                else:
                    WYT = 1

        self.WYT = WYT

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
