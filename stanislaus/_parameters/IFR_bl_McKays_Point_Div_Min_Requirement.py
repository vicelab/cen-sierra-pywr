import datetime
from parameters import MinFlowParameter
from utilities.converter import convert


class IFR_bl_McKays_Point_Div_Min_Requirement(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        ifr_val = 18 / 35.31  # cfs to cms; 16.5 cfs req't, min 18 cfs in practice
        if self.model.mode == 'scheduling':
            ifr_val = self.get_down_ramp_ifr(timestep, scenario_index, ifr_val, rate=0.25)
        else:
            ifr_val *= self.days_in_month
        return ifr_val

    def value(self, *args, **kwargs):
        try:
            ifr = self.get_ifr(*args, **kwargs)
            if ifr is not None:
                return ifr
            else:
                ifr = self._value(*args, **kwargs)
                return convert(ifr, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_McKays_Point_Div_Min_Requirement.register()
print(" [*] IFR_bl_McKays_Point_Div_Min_Requirement successfully registered")
