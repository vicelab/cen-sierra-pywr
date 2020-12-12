from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Lyons_Res_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT = self.get("San Joaquin Valley WYT" + self.month_suffix, timestep, scenario_index)
        WYI = self.get("San Joaquin Valley WYI" + self.month_suffix, timestep, scenario_index)

        # IFR is in cfs

        # Really dry year; PG&E has asked for temporary reductions in the past
        if WYI < 2 and (self.datetime.month >= 8 or self.datetime.month <= 3):
            ifr = 2.75

        # regular IFR schedule
        elif WYT == 1:
            ifr = 5
        else:
            month = self.datetime.month  # not necessary, but a little easier to read
            if month == 10:  # Oct
                ifr = 8
            elif month >= 11 or month <= 6:  # Nov-Jun
                ifr = 10
            elif month == 7:  # July
                ifr = 8
            else:  # Aug-Sep
                ifr = 5
        ifr *= self.cfs_to_cms
        if self.mode == 'planning':
            ifr *= self.days_in_month
        return ifr

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Lyons_Res_Requirement.register()
