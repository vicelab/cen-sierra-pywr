from parameters import WaterLPParameter
from dateutil.relativedelta import relativedelta


class Oakdale_Irrigation_District_Demand(WaterLPParameter):

    def _value(self, timestep, scenario_index):

        if not 3 <= self.datetime.month <= 10:
            return 0  # Only deliver Mar-Oct based on observed data

        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        demand_mcm_df = self.model.tables["Oakdale Irrigation District Demand"][WYT]
        start = int(self.datetime.strftime('%j'))
        if self.model.mode == 'scheduling':
            demand_mcm = demand_mcm_df[start]
        else:
            offset_days = self.days_in_month() - 1
            end = int((self.datetime + relativedelta(days=+offset_days)).strftime('%j'))
            demand_mcm = demand_mcm_df[start - 1:end - 1].sum()
        return demand_mcm

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


Oakdale_Irrigation_District_Demand.register()
print(" [*] Oakdale_Irrigation_District_Demand successfully registered")
