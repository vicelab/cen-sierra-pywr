from parameters import WaterLPParameter

from utilities.converter import convert
from dateutil.relativedelta import relativedelta
from calendar import isleap
import random


class PH_Water_Demand(WaterLPParameter):
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
        param = self.res_name + '/Turbine Capacity' + self.month_suffix
        # turbine capacity is already in mcm
        turbine_capacity = self.model.parameters[param].value(timestep, scenario_index) / 0.0864

        price_year = int(self.model.parameters['Price Year'].value(timestep, scenario_index))

        if self.datetime.month == 2 and self.datetime.day == 29:
            price_date = self.datetime.strftime('{}-02-28'.format(price_year))
        else:
            price_date = self.datetime.strftime('{}-%m-%d'.format(price_year))

        # calculate the price threshold if needed
        if self.model.mode == 'planning':
            block = self.model.tables["Energy Price Blocks"].at[price_date, str(self.block)]
            turbine_capacity *= self.days_in_month()

        elif self.model.planning:

            # TODO: move as much of this as possible to a single parameter

            if timestep.day == 1:
                end = timestep.datetime + relativedelta(months=+1) - relativedelta(days=+1)
                if not isleap(price_year) and timestep.month == 2:
                    price_end = '{}-02-28'.format(price_year)
                else:
                    price_end = end.strftime('{}-%m-%d'.format(price_year))
                energy_prices = all_energy_prices[price_date:price_end].values.flatten()
                energy_prices[::-1].sort()  # sort in descending order
                planning_release = self.model.planning.nodes[self.res_name + '/1'].flow[-1]

                # for planning turbine capacity, note that the turbine capacities are the same
                # in both models (i.e., cms)
                planning_turbine_capacity = turbine_capacity * self.cms_to_mcm * (end - self.datetime).days
                planning_release_fraction = min(planning_release / planning_turbine_capacity, 1.0)
                price_index = int(len(energy_prices) * planning_release_fraction) - 1
                if price_index < 0:
                    self.price_threshold = 1e6  # no production this month (unlikely)
                else:
                    self.price_threshold = energy_prices[price_index]

            # calculate today's total release
            energy_prices_today = all_energy_prices.loc[price_date].values
            if self.block == 1:
                production_hours = len([1 for p in energy_prices_today if p >= self.price_threshold])
            else:
                production_hours = len([1 for p in energy_prices_today if 0.0 < p < self.price_threshold])

            max_flow_fraction = production_hours / 24
            # blocks = self.model.tables["Energy Price Blocks"].loc[timestep.datetime]

            # sum_of_previous_blocks = blocks[:str(self.block - 1)].sum()
            # allocation_remaining = max_flow_fraction - sum_of_previous_blocks
            # allocation_to_this_block = min(allocation_remaining, blocks[str(self.block)])
            # block = max(allocation_to_this_block, 0.0)
            block = max_flow_fraction

        else:
            block = self.model.tables["Energy Price Blocks"].at[price_date, str(self.block)]

        # TODO: Extend the following to planning mode
        if self.res_name == 'Collierville PH' and self.block == 1:
            block = max(block, 0.05 + random.random() * 0.05)

        elif self.res_name in ['Sand Bar PH', 'Stanislaus PH']:
            if self.model.mode == 'scheduling' \
                    and (11, 1) <= (self.datetime.month, self.datetime.day) <= (11, 14):
                turbine_capacity = 0.0
            elif self.model.mode == 'planning' and self.datetime.month == 11:
                turbine_capacity *= 0.5

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


PH_Water_Demand.register()
print(" [*] PH_Water_Demand successfully registered")
