from parameters import WaterLPParameter

from utilities.converter import convert
import datetime as dt


class Millerton_Lake_Storage_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        rule_curve_mcm = self.model.tables["Millerton Lake rule curve"]
        # start = self.datetime.strftime('%b-%d')
        start = (self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            control_curve_target = rule_curve_mcm[start]
        else:
            end = (self.datetime.month, self.days_in_month())
            control_curve_target = rule_curve_mcm[start:end].mean()
        max_storage = self.model.nodes["Millerton Lake" + self.month_suffix].max_volume
        return control_curve_target / max_storage
        # return control_curve_target

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


Millerton_Lake_Storage_Demand.register()
print(" [*] Millerton_Lake_Storage_Demand successfully registered")
