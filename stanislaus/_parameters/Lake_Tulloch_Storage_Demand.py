from parameters import WaterLPParameter

from utilities.converter import convert
import pandas as pd


class Lake_Tulloch_Storage_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        flood_control_req = self.model.tables["Lake Tulloch Flood Control"]
        start = '{}-{}'.format(self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            control_curve_target = flood_control_req[start]
        else:
            end = '{}-{}'.format(self.datetime.month, self.days_in_month)
            control_curve_target = flood_control_req[start:end].mean()
        max_storage = self.model.nodes["Lake Tulloch" + self.month_suffix].max_volume
        return control_curve_target / max_storage

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


Lake_Tulloch_Storage_Demand.register()
print(" [*] Lake_Tulloch_Storage_Demand successfully registered")
