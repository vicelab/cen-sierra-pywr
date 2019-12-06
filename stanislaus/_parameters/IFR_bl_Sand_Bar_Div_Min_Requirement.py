import datetime
from parameters import WaterLPParameter
from utilities.converter import convert


class IFR_bl_Sand_Bar_Div_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT_table = self.model.tables["WYT P2005 & P2130"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1

        WYT = WYT_table[operational_water_year]
        management = "BAU"

        schedule = self.model.tables["IFR Below Sand Bar Div Schedule"]

        if self.datetime.month >= 10:
            dt = datetime.date(1999, self.datetime.month, self.datetime.day)
        else:
            dt = datetime.date(2000, self.datetime.month, self.datetime.day)

        # Critically Dry: 1,Dry: 2,Normal-Dry: 3,Normal-Wet: 4,Wet: 5
        ifr_val = float(schedule[(schedule['start_date'] <= dt) & (schedule['end_date'] >= dt)][str(WYT)]) / 35.314666

        # Calculate supp IFR
        ifr_supp = 0
        data_supp = self.model.tables["Supplemental IFR below Sand Bar Div"]
        if self.mode == 'scheduling':
            if self.datetime.month == 10 and self.datetime.day == 1:
                self.peak_dt = self.model.tables["Peak Donnells Runoff"][timestep.year + 1]
            diff_day = (self.datetime - self.peak_dt).days
            if 0 < diff_day <= 91:
                ifr_supp = \
                    (data_supp[(data_supp['Day_st'] < diff_day) & (diff_day <= data_supp['Day_end'])][str(WYT)]) \
                        .values[-1] / 35.314666
            ifr_val += ifr_supp

            ifr_val = self.get_down_ramp_ifr(timestep, 0.0, initial_value=80 / 35.31, rate=0.25)

        else:
            if self.datetime.month == 5:
                ifr_supp = data_supp[str(WYT)].loc[0:4].mean()
            elif self.datetime.month == 6:
                ifr_supp = data_supp[str(WYT)].loc[5:8].mean()
            elif self.datetime.month == 7:
                ifr_supp = data_supp[str(WYT)].loc[8:12].mean()
            else:
                ifr_supp = 0

            ifr_val += ifr_supp

        return ifr_val

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
