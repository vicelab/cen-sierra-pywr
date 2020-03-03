from parameters import WaterLPParameter

from utilities.converter import convert


class SFPUC_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # annual_demand_mcm = 15913 * 0.0864 / 4.5
        annual_demand_mcm = 205 * 3.57 / 1000 * 1.2335 * 365.24

        week = min(timestep.datetime.week, 52)
        daily_fraction = self.model.tables["SFPUC weekly fraction"][week] / 7
        daily_demand_cms = annual_demand_mcm * daily_fraction / 0.0864

        return daily_demand_cms

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


SFPUC_Demand.register()
print(" [*] SFPUC_Demand successfully registered")
