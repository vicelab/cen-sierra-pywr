import datetime
from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_below_Goodwin_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        year_type = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        timestep_date = timestep.datetime
        current_date = datetime.datetime(2000, timestep_date.month, timestep_date.day)
        if datetime.datetime(2000, 10, 1) < current_date < datetime.datetime(2000, 12, 31):
            if year_type == 1 or year_type == 2:
                return 4.25
            else:
                return 5.66
        elif datetime.datetime(2000, 1, 1) < current_date < datetime.datetime(2000, 5, 31):
            if year_type == 1 or year_type == 2:
                return 2.83
            else:
                return 3.54
        else:
            if year_type == 1 or year_type == 2:
                return 1.42
            else:
                return 2.83

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


node_IFR_below_Goodwin_Reservoir_Requirement.register()
print(" [*] node_IFR_below_Goodwin_Reservoir_Requirement successfully registered")
