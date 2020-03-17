import datetime
import numpy as np
from parameters import WaterLPParameter
from utilities.converter import convert


class IFR_bl_Sand_Bar_Div_Min_Requirement(WaterLPParameter):
    """"""
    def setup(self):
        super.setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.peak_dt = np.ones([num_scenarios], np.float)

    def _value(self, timestep, scenario_index):

        WYT = self.model.tables["WYT P2005 & P2130"][self.operational_water_year]
        schedule = self.model.tables["IFR Below Sand Bar Div Schedule"]

        month = self.datetime.month
        if self.model.mode == 'scheduling':
            day = self.datetime.day
            start_day = 1
            start_month = month
            if (2, 10) <= (month, day) <= (5, 31):
                start_day = 10
            if month in [2, 3, 4, 5] and day <= 9:
                start_month -= 1
            ifr_cms = schedule.at[(start_month, start_day), WYT] / 35.31

        else:
            ifr_cms = schedule.at[(month, 1), WYT] / 35.31

        # Calculate supp IFR

        if self.mode == 'scheduling':
            if self.datetime.month == 10 and self.datetime.day == 1:
                self.peak_dt = self.model.tables["Peak Donnells Runoff"][timestep.year + 1]
            diff_day = (self.datetime - self.peak_dt).days
            if 0 <= diff_day < 91:
                data_supp = self.model.tables["Supplemental IFR below Sand Bar Div"]
                start_idx = diff_day - diff_day % 7
                ifr_cms += data_supp.at[start_idx, WYT] / 35.31
            ifr_cms = self.get_down_ramp_ifr(timestep, scenario_index, ifr_cms, rate=0.25)

        else:
            data_supp = self.model.tables["Supplemental IFR below Sand Bar Div"]
            if self.datetime.month == 5:
                supp_cfs = data_supp[WYT].iloc[0:4].mean()
            elif self.datetime.month == 6:
                supp_cfs = data_supp[WYT].iloc[5:8].mean()
            elif self.datetime.month == 7:
                supp_cfs = data_supp[WYT].iloc[8:12].mean()
            else:
                supp_cfs = 0

            ifr_cms = (ifr_cms + supp_cfs / 35.31) * self.days_in_month()

        return ifr_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Sand_Bar_Div_Min_Requirement.register()
print(" [*] IFR_bl_Sand_Bar_Div_Requirement successfully registered")
