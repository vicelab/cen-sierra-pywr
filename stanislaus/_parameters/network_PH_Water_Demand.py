from parameters import WaterLPParameter

from utilities.converter import convert
from dateutil.relativedelta import relativedelta


class network_PH_Water_Demand(WaterLPParameter):
    """"""

    price_threshold = 20.0  # an arbitrary first value
    cms_to_mcm = 0.0864

    def __init__(self, model, node, block, **kwargs):
        super().__init__(model, **kwargs)
        self.node = node
        self.block = block

    def _value(self, timestep, scenario_index, mode='scheduling'):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        all_energy_prices = self.model.tables['All Energy Price Values']
        turbine_capacity = self.model.parameters[self.res_name + '/Turbine Capacity'] \
            .value(timestep, scenario_index)
        # calculate the price threshold if needed
        if self.model.mode == 'planning':
            block = self.model.tables["Energy Price Blocks"].at[timestep.datetime, str(self.block)]
            turbine_capacity *= self.days_in_month()

        elif self.model.planning:

            if timestep.day == 1:
                start = timestep.datetime
                end = start + relativedelta(months=+1) - relativedelta(days=+1)
                energy_prices = all_energy_prices[start:end].values.flatten()
                energy_prices[::-1].sort()  # sort in descending order
                planning_release = self.model.planning.nodes[self.res_name + '/1'].flow[-1]

                # for planning turbine capacity, note that the turbine capacities are the same
                # in both models (i.e., cms)
                planning_turbine_capacity = turbine_capacity * self.cms_to_mcm * (end - start).days
                planning_release_fraction = min(planning_release / planning_turbine_capacity, 1.0)
                price_index = int(len(energy_prices) * planning_release_fraction) - 1
                if price_index < 0:
                    self.price_threshold = 1e6  # no production this month (unlikely)
                else:
                    self.price_threshold = energy_prices[price_index]

            # calculate today's total release
            energy_prices_today = all_energy_prices.loc[timestep.datetime].values
            production_hours = len([1 for p in energy_prices_today if p >= self.price_threshold])
            max_flow_fraction = production_hours / 24

            blocks_as_strings = [str(b) for b in range(1, self.block+1)]
            blocks = self.model.tables["Energy Price Blocks"][blocks_as_strings].loc[timestep.datetime]

            sum_of_blocks = 0
            block = 0
            for b in blocks_as_strings:
                sum_of_blocks += blocks[b]
                if sum_of_blocks > max_flow_fraction:
                    if block == self.block:
                        block = sum_of_blocks - max_flow_fraction
                    else:
                        block = 0.0
                else:
                    block = blocks[b]

        else:
            block = self.model.tables["Energy Price Blocks"].at[timestep.datetime, str(self.block)]

        demand_mcm = turbine_capacity * self.cms_to_mcm * block

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
