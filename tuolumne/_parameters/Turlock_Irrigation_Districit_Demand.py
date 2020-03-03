from parameters import WaterLPParameter

from utilities.converter import convert


class Turlock_Irrigation_District_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT_names = ["Critical", "Dry", "Below", "Above", "Wet"]
        SJV_WYT = self.model.parameters["San Joaquin Valley WYT"].value(timestep, scenario_index)
        dm = (timestep.month, timestep.day)
        demand_cfs = self.model.tables["Turlock Irrigation District/Demand Table"].at[dm, WYT_names[SJV_WYT - 1]]

        return demand_cfs / 35.315

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000)
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


Turlock_Irrigation_District_Demand.register()
print(" [*] Turlock_Irrigation_District_Demand successfully registered")
