import datetime
import calendar
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_Hunter_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        # if datetime.date(timestep.year,5,1) <= timestep.datetime <= datetime.date(timestep.year,10,31):
        if 5 <= timestep.month <= 10:  # May-Oct
            # ifr_val = 0.042475 # cms (1.5 cfs)
            ifr_val = 1.5
        else:
            # ifr_val = 0.014158 #cms (0.5 cfs)
            ifr_val = 0.5
        # NOTE: the above can be written as
        # ifr = 1.5 if 5 <= timestep.month <= 10 else 0.5, though it's less intuitive
        ifr_val *= self.cfs_to_cms

        if self.mode == 'planning':
            ifr_val *= self.days_in_month()
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


node_IFR_bl_Hunter_Reservoir_Requirement.register()
print(" [*] node_IFR_bl_Hunter_Reservoir_Requirement successfully registered")
