from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Millerton_Lake_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # get WYT index
        if 3 >= self.datetime.month:
            restoration_year = self.datetime.year
        else:
            restoration_year = self.datetime.year - 1
        wyt_index = self.model.tables["WYT below Friant Dam"][restoration_year]

        # get date index
        ifr_schedule_cfs = self.model.tables["IFR Schedule below Friant Dam"]
        day_month = (self.datetime.year, self.datetime.month)
        if self.model.mode == 'planning':
            date_index = self.datetime.month - 1
        else:
            date_index = sum([1 for dm in ifr_schedule_cfs.index if day_month >= dm]) - 1

        # get IFR from schedule
        ifr_cfs = ifr_schedule_cfs.iat[date_index, wyt_index]

        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month()
        
        return ifr_cfs / 35.31
        
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
        
IFR_bl_Millerton_Lake_Min_Flow.register()
print(" [*] IFR_bl_Millerton_Lake_Min_Flow successfully registered")
