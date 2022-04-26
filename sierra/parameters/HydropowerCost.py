from sierra.base_parameters import BaseParameter
from calendar import isleap


class HydropowerCost(BaseParameter):
    """"""

    # path = "s3_imports/energy_netDemand.csv"

    # baseline_median_daily_energy_demand = 768  # 768 GWh is median daily energy demand for 2009

    def _value(self, timestep, scenario_index):

        # per-mcm value is a function of:
        # 1. electricity price
        # 2. generating potential, a function of generating efficiency, head, etc.

        price_year = int(self.model.parameters['Price Year'].value(timestep, scenario_index))

        if isleap(self.datetime.year) and self.datetime.month == 2 and self.datetime.day == 29:
            price_date = self.datetime.strftime('{}-02-28'.format(price_year))
        else:
            price_date = self.datetime.strftime('{}-%m-%d'.format(price_year))

        # price_per_kWh = self.model.tables["Energy Price Values"] \
        #     .at[price_date, str(self.block)]
        # head = self.model.nodes[self.res_name + self.month_suffix].head
        # eta = 0.9  # generation efficiency
        # gamma = 9807  # specific weight of water = rho*g
        # price_per_mcm = price_per_kWh * gamma * head * eta * 24 / 1e6
        #
        # pywr_cost = - (abs(price_per_mcm) / 100 + 100) * price_per_mcm / abs(price_per_mcm)

        resource_blocks = self.model.blocks.get(self.res_attr_name)

        if self.model.mode == 'planning':
            powerhouse = self.model.nodes[self.res_name + self.month_suffix]
            price_per_kWh = self.model.tables["Energy Price Values"] \
                .at[price_date, str(self.block)]
            eta = 0.9  # generation efficiency
            gamma = 9807  # specific weight of water = rho*g
            price_per_mcm = price_per_kWh * gamma * powerhouse.head * eta * 24 / 1e6

            # We can add some conversion function here to go from price to Pywr cost
            # For now, divide by 100, which results in costs of about -5 to -170
            # E-flow costs can be set to less than this, or say -1000
            pywr_cost = - (abs(price_per_mcm) / 100 + 100) * price_per_mcm / abs(price_per_mcm)
            # if pywr_cost > 0 and self.res_name == 'Collierville PH':
            #     pywr_cost *= 1000
            if self.block == 1:
                pywr_cost = min(pywr_cost, powerhouse.residual_cost)
        else:
            powerhouse = self.model.nodes[self.res_name]
            if self.block == resource_blocks[-1]:
                pywr_cost = 1  # costs money to generate in block 3 (negative prices)
            elif self.block == resource_blocks[0]:
                pywr_cost = powerhouse.residual_cost
            else:
                pywr_cost = -100

        return pywr_cost

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


HydropowerCost.register()
