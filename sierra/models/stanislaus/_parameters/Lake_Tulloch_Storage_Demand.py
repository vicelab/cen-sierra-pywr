from sierra.base_parameters import BaseParameter


class Lake_Tulloch_Storage_Demand(BaseParameter):

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
        val = self._value(*args, **kwargs)
        return val

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_Tulloch_Storage_Demand.register()
