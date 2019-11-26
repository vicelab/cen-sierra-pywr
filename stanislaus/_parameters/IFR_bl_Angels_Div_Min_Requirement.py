import datetime
import calendar
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Angels_Div_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 0.14158 * 1.1  # cms (5 cfs) w/ 10% factor of safety
        # if self.model.mode == 'scheduling':
        #     # IFR is max of 75% of previous flow Qp and IFR
        #     if timestep.index == 0:
        #         Qp = ifr_val
        #     else:
        #         Qp = self.model.nodes[self.res_name].prev_flow[-1] / 0.0864  # convert to cms
        #     ifr_val = max(ifr_val, Qp * 0.75)
        # else:
        #     ifr_val *= self.days_in_month()
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


IFR_bl_Angels_Div_Min_Requirement.register()
print(" [*] IFR_bl_Angels_Div_Min_Requirement successfully registered")
