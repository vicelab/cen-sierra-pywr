from sierra.base_parameters import BaseParameter


class Lake_Tulloch_Min_Volume(BaseParameter):

    def _value(self, timestep, scenario_index):
        flood_control_req = self.model.tables["Lake Tulloch Flood Control"]
        start = '{}-{}'.format(self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            control_curve_target = flood_control_req[start]
        else:
            end = '{}-{}'.format(self.datetime.month, self.days_in_month)
            control_curve_target = flood_control_req[start:end].mean()
        return control_curve_target - 1.62  # subtract 2 TAF based on observations

    def value(self, *args, **kwargs):
        val = self._value(*args, **kwargs)
        return val

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_Tulloch_Min_Volume.register()
