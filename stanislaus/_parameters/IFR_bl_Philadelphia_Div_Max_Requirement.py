import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Philadelphia_Div_Max_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        max_flow = 50 / 35.31  # IFR max is 60 cfs; 50 cfs in practice
        if self.model.mode == 'scheduling':
            ifr_range = self.get_ifr_range(
                timestep, scenario_index,
                initial_value=(10 / 35.31), max_flow=max_flow, rate=3.0)
        else:
            ifr_range = self.get_ifr_range(
                timestep, scenario_index, max_flow=max_flow, rate=6.0)
        return ifr_range

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


IFR_bl_Philadelphia_Div_Max_Requirement.register()
print(" [*] IFR_bl_Philadelphia_Div_Max_Requirement successfully registered")
