from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert

class Friant_Kern_Canal_Demand_Demand(BaseParameter):
    """"""
    FKCD_bias_factor = 1.23
    
    def _value(self, timestep, scenario_index):
        
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        df = self.model.tables["CVP Friant-Kern Canal demand"]*self.FKCD_bias_factor
        col = df.columns[WYT - 1]
        demand_cfs = df[col]  # data is currently in cfs
        
        today = (self.datetime.month, self.datetime.day)

        if self.model.mode == 'scheduling':
            demand_cms = demand_cfs[today] / 35.31

        else:
            end = (self.datetime.month, self.days_in_month)
            demand_cms = demand_cfs[today:end].sum() / 35.31
        
        return demand_cms
        
    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
Friant_Kern_Canal_Demand_Demand.register()
