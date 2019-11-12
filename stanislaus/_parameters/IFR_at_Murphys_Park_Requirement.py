import datetime
import calendar
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_at_Murphys_Park_Requirement(WaterLPParameter):
    """"""
    year_type_thresholds = [100000, 140000, 320000, 400000, 500000]
    may_sep = [12, 16, 22, 26, 30]
    oct_mar = [12, 12, 16, 18, 18]
    apr = [12, 16, 22, 26, 30]
    year_type = 5  # initial water year (for WY2009)

    def _value(self, timestep, scenario_index):
        month = self.datetime.month
        mode = self.model.mode

        # Calculate water year type based on Apr-Jul inflow forecast
        if month == 5 and self.datetime.day == 1:

            start = '{:04}-04-01'.format(self.datetime.year)
            end = '{:04}-07-31'.format(self.datetime.year)
            total_runoff = 0
            for j in range(1, 26):
                if mode == 'scheduling':
                    runoff = self.model.parameters['STN_{:02} Headflow/Runoff'.format(j)].dataframe[start:end].sum()
                else:
                    runoff = self.model.parameters['STN_{:02} Headflow/Runoff/1'.format(j)].dataframe[start:end].sum()
                total_runoff += runoff / 1.2335 * 1000
            self.year_type = len([x for x in self.year_type_thresholds if total_runoff >= x])

        # Determine schedule based on time of year
        if 5 <= month <= 9:  # May-Sep
            schedule = self.may_sep
        elif month >= 10 or month <= 3:
            schedule = self.oct_mar
        else:
            schedule = self.apr

        # Get the IFR from the schedule based on year type
        ifr_val = schedule[self.year_type - 1] / 35.31  # convert cfs to cms

        if self.model.mode == 'planning':
            ifr_val *= self.days_in_month()

        if month == 11:  # reduce flow for maintenance in early November
            if mode == 'scheduling' and timestep.day <= 14:
                ifr_val = 2 / 35.31  # set IFR to 2 cfs converted to cms
            elif mode == 'planning':
                ifr_val = ifr_val - (0.0685 / 0.0864)  # subtract 2 cfs for 14 days

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


IFR_at_Murphys_Park_Requirement.register()
print(" [*] IFR_bl_Angels_Div_Requirement successfully registered")
