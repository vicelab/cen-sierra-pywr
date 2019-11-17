import datetime
import calendar
from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Collierville_PH_discharge_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.mode == 'scheduling':
            # get previous flow
            if timestep.index == 0:
                Qp = 0.4  # TODO: this needs to be from observed data
            else:
                Qp = self.model.nodes[self.res_name].flow[-1]
            min_flow = Qp * 0.75
            return min_flow

        if self.mode == 'planning':
            # no constraint
            return 0.0

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


IFR_bl_Collierville_PH_discharge_Min_Requirement.register()
print(" [*] IFR_bl_Collierville_PH_discharge_Min_Requirement successfully registered")
