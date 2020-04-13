from parameters import WaterLPParameter

from utilities.converter import convert


class Modesto_Irrigation_District_Demand(WaterLPParameter):
    """"""
    WYT_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def _value(self, timestep, scenario_index):

        SJV_WYT = self.model.parameters["San Joaquin Valley WYT"].value(timestep, scenario_index)
        demand_fraction = self.model.tables["Modesto Irrigation District/Demand Table"]\
            .at[(timestep.month, timestep.day), self.WYT_names[SJV_WYT - 1]]

        # Assume MID annual demand is 300,000 AF = 370.1 mcm
        TID_annual_demand_mcm = 370.1
        demand_cms = demand_fraction * TID_annual_demand_mcm / 0.0864
        return demand_cms

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


Modesto_Irrigation_District_Demand.register()
print(" [*] Modesto_Irrigation_District_Demand successfully registered")
