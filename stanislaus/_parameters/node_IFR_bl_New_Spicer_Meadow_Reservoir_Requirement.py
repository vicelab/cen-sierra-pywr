import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_New_Spicer_Meadow_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 0.4672  # cms (16.5 cfs)
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


node_IFR_bl_New_Spicer_Meadow_Reservoir_Requirement.register()
print(" [*] node_IFR_bl_New_Spicer_Meadow_Reservoir_Requirement successfully registered")
