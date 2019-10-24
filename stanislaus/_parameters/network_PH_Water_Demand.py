from parameters import WaterLPParameter

from utilities.converter import convert


class network_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index, mode='scheduling'):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)

        nblocks = self.model.parameters['Blocks'].value(timestep, scenario_index)
        q_demand = self.model.parameters['node/' + self.res_name + '/Turbine Capacity'] \
                       .value(timestep, scenario_index) * 3600 * 24 / nblocks

        if mode == 'planning':
            q_demand *= self.days_in_month()

        return q_demand

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index, mode=self.mode) / 1e6
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


network_PH_Water_Demand.register()
print(" [*] network_PH_Water_Demand successfully registered")
