from parameters import WaterLPParameter

from utilities.converter import convert


class Big_Creek_System_IFRs_2000(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        month = self.datetime.month

        Friant_Apr_Jul_runoff_af = self.model.tables['Seasonal Inflow at Friant'][self.operational_water_year]
        if Friant_Apr_Jul_runoff_af <= 900000:
            ifr_table = self.model.tables['Big Creek System IFRs 2000 dry']
        else:
            ifr_table = self.model.tables['Big Creek System IFRs 2000 normal']

        col_name = month
        if self.model.mode == 'scheduling':
            if month in [11, 12, 4, 9]:
                day = self.datetime.day
                col_name = '{}-{}'.format(month, min(day - day % 15 + 1, 16))

        ifr_cfs = ifr_table.at[self.res_name, col_name]

        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month()

        return ifr_cfs / 35.315

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


Big_Creek_System_IFRs_2000.register()
print(" [*] Big_Creek_System_IFRs_2000 successfully registered")
