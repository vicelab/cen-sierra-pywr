from parameters import WaterLPParameter

from utilities.converter import convert


class network_PH_Water_Demand(WaterLPParameter):
    """"""

    def __init__(self, model, node, block, **kwargs):
        super().__init__(model, **kwargs)
        self.node = node
        self.block = block

    def _value(self, timestep, scenario_index, mode='scheduling'):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)

        block = self.model.tables["Energy Price Blocks"].at[timestep.datetime, str(self.block)]
        turbine_capacity = self.model.parameters[self.res_name + '/Turbine Capacity']\
            .value(timestep, scenario_index)
        demand_mcm = turbine_capacity * block * 3600 * 24 / 1e6

        if mode == 'planning':
            demand_mcm *= self.days_in_month()

        return demand_mcm

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index, mode=self.mode)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        node = data.pop('node', None)
        block = data.pop('block', None)
        return cls(model, node, block, **data)


network_PH_Water_Demand.register()
print(" [*] network_PH_Water_Demand successfully registered")
