import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Relief_Reservoir_Max_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        if self.model.mode == 'scheduling':
            ifr_max = self.get_up_ramp_ifr(timestep, initial_value=(30 / 35.31), rate=0.25)
        else:
            ifr_max = 1e6
        return ifr_max

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


IFR_bl_Relief_Reservoir_Max_Requirement.register()
print(" [*] IFR_bl_Relief_Reservoir_Requirement successfully registered")
