from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Redinger_Lake_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        month = self.datetime.month
        year_type = self.model.parameters["San Joaquin Valley WYT" + self.month_suffix].value(timestep, scenario_index)
        return_val = 0
        
        if month in [10, 11, 12, 1, 2, 3, 4] and year_type in [1,2]: # October - April and Dry or Critical
            return_val = 15
        else:
            return_val = 20
        
        if self.model.mode == "planning":
            return_val *= self.days_in_month()
        
        return return_val
        
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
        
IFR_bl_Redinger_Lake_Min_Flow.register()
print(" [*] IFR_bl_Redinger_Lake_Min_Flow successfully registered")
