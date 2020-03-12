import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_NF_Stanislaus_Div_Res_Min_Requirement(WaterLPParameter):
    """"""

    initial_value= (16.5/35.31)


    def _value(self, timestep, scenario_index):
        ifr_val = self.initial_value # cfs to cms (16.5 cfs)
        if self.model.mode == 'scheduling':
            ifr_val = self.get_down_ramp_ifr(timestep, scenario_index, ifr_val, self.initial_value, rate=0.25)
        if self.model.mode == 'planning':
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


IFR_bl_NF_Stanislaus_Div_Res_Min_Requirement.register()
print(" [*] IFR_bl_NF_Stanislaus_Div_Res_Min_Requirement successfully registered")
