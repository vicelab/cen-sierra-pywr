import datetime
from parameters import WaterLPParameter

from utilities.converter import convert
from dateutil.relativedelta import relativedelta


class Water_Supply_Release_bl_New_Spicer_Meadow_Reservoir(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        water_supply_reqt = self.model.tables["District Demand below New Spicer Meadow"]
        start = '{}-{}'.format(self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            max_flow = water_supply_reqt[start] / 35.31
        else:
            end = '{}-{}'.format(self.datetime.month, self.days_in_month())
            max_flow = water_supply_reqt[start:end].sum() / 35.31  # cfs to cms

        # modify max_flow up/down based on regression
        # y = -0.0299x2 + 0.5624x where x = SJVI and y = % of mean.
        SJVI = self.get("San Joaquin Valley WYI" + self.month_suffix)
        scaling_factor = -0.0299 * SJVI ** 2 + 0.5624 * SJVI
        max_flow = max_flow * scaling_factor
        return max_flow

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Water_Supply_Release_bl_New_Spicer_Meadow_Reservoir.register()
print(" [*] Water_Supply_Release_bl_New_Spicer_Meadow_Reservoir successfully registered")
