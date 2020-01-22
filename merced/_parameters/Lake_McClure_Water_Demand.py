from parameters import WaterLPParameter

from utilities.converter import convert


class Lake_McClure_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if (timestep.month, timestep.day) == (10, 1):
            SJVI = self.model.tables["San Joaquin Valley Index"][timestep.year + 1]

            if SJVI <= 2.5:
                self.wyt = 'dry'
            elif SJVI < 3.8:
                self.wyt = 'normal'
            else:
                self.wyt = 'wet'

        curves_af = self.model.tables["Lake McClure/Guide Curve"]
        max_volume_mcm = self.model.nodes[self.res_name].max_volume.get_value(scenario_index)
        date_str = '1900-{:02}-{:02}'.format(timestep.month, timestep.day)
        target_mcm = curves_af.at[date_str, self.wyt] * 1233.5 / 1e6
        target_fraction = min(target_mcm / max_volume_mcm, 1.0)
        return target_fraction

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_McClure_Water_Demand.register()
print(" [*] Lake_McClure_Water_Demand successfully registered")
