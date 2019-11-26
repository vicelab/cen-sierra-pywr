from parameters import WaterLPParameter

from utilities.converter import convert
import pandas as pd


class Tulloch_Lake_Storage_Value(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        path = "Management/BAU/Flood Control/LakeTulloch_FloodControl_Requirement.csv"
        flood_control_req = self.read_csv(path, index_col=[0], parse_dates=False, squeeze=True)
        start = self.datetime.strftime('%m-%d')
        if self.model.mode == 'scheduling':
            control_curve_target = flood_control_req[start]
        else:
            end = '{:02}-{:02}'.format(self.datetime.month, self.days_in_month())
            control_curve_target = flood_control_req[start:end].mean()
        max_storage = self.model.nodes["Tulloch Lake" + self.month_suffix].max_volume
        return control_curve_target / max_storage

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Tulloch_Lake_Storage_Value.register()
print(" [*] Tulloch_Lake_Storage_Value successfully registered")
