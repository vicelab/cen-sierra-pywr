import datetime
from parameters import MaxFlowParameter

from utilities.converter import convert


class IFR_bl_Donnell_Lake_Max_Requirement(MaxFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        if self.model.mode == 'scheduling':
            ifr_range = self.get_ifr_range(
                timestep, scenario_index,
                initial_value=25 / 35.31, rate=0.25, max_flow=60 / 35.31)
        else:
            ifr_range = 1e6
        return ifr_range

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


IFR_bl_Donnell_Lake_Max_Requirement.register()
print(" [*] IFR_bl_Donnell_Lake_Max_Requirement successfully registered")
