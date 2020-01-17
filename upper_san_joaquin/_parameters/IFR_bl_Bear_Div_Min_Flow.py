from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Bear_Div_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        year_type = self.get("San Joaquin Valley WYT" + self.month_suffix)
        month = self.datetime.month
        ifr_cfs = 0

        if year_type in [1, 2]:  # Critical or Dry WYT
            if month in [5, 6, 7, 8, 9]:
                ifr_cfs = 2
            else:
                ifr_cfs = 1
        else:
            if month in [5, 6, 7, 8, 9]:
                ifr_cfs = 3
            else:
                ifr_cfs = 2

        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month()

        return ifr_cfs / 35.31

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
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


IFR_bl_Bear_Div_Min_Flow.register()
print(" [*] IFR_bl_Bear_Div_Min_Flow successfully registered")
