from sierra.base_parameters import BaseParameter
from dateutil.relativedelta import relativedelta


class Oakdale_Irrigation_District_Demand(BaseParameter):

    OID_bias_factor = 1.02
    
    def _value(self, timestep, scenario_index):

        if not 3 <= self.datetime.month <= 10:
            return 0  # Only deliver Mar-Oct based on observed data
        
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        demand_mcm_df = self.model.tables["Oakdale Irrigation District Demand"][WYT]*self.OID_bias_factor
        start = (self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            demand_mcm = demand_mcm_df[start]
        else:
            end_date = self.datetime + relativedelta(days=+(self.days_in_month-1))
            demand_mcm = demand_mcm_df[start:(end_date.month, end_date.day)].sum()
        return demand_mcm

    def value(self, *args, **kwargs):
        val = self._value(*args, **kwargs)
        return val

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Oakdale_Irrigation_District_Demand.register()
