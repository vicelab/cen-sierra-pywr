from parameters import WaterLPParameter


class network_PH_Cost(WaterLPParameter):
    """"""

    # path = "s3_imports/energy_netDemand.csv"

    # baseline_median_daily_energy_demand = 768  # 768 GWh is median daily energy demand for 2009

    def _value(self, timestep, scenario_index):

        # if timestep.index == 0:
        #     self.nblocks = self.model.parameters["Blocks"].get_value(scenario_index)
        #     self.demandParam = self.model.parameters[self.res_name + '/Demand Constant'].value(timestep, scenario_index)

        # totDemandP = self.model.parameters["Total Net Energy Demand"]
        # maxDemandP = self.model.parameters["Max Net Energy Demand"]
        # minDemandP = self.model.parameters["Min Net Energy Demand"]

        # if self.mode == 'scheduling':
        #     days_in_period = 1
        #     totDemand = totDemandP.value(timestep, scenario_index)
        #     minDemand = maxDemandP.value(timestep, scenario_index)
        #     maxDemand = maxDemandP.value(timestep, scenario_index)
        #
        # else:
        #     planning_dates = self.dates_in_month()
        #     days_in_period = len(planning_dates)
        #     totDemand = totDemandP.dataframe[planning_dates].sum()
        #     minDemand = minDemandP.dataframe[planning_dates].min()
        #     maxDemand = maxDemandP.dataframe[planning_dates].max()
        #
        # baselineDemand = self.baseline_median_daily_energy_demand * days_in_period
        # minVal = self.demandParam * (totDemand / baselineDemand)
        # maxVal = minVal * (maxDemand / minDemand)
        # max_min_diff = maxVal - minVal
        #
        # value = maxVal - ((max_min_diff / (2 * self.nblocks)) * (self.block * 2 - 1))

        # per-mcm value is a function of:
        # 1. electricity price
        # 2. generating potential, a function of generating efficiency and head

        price_per_kWh = self.model.tables["Price Values"].at[timestep.datetime, str(self.block)]
        head = self.model.nodes[self.res_name].head
        eta = 0.9  # generation efficiency
        gamma = 9807  # specific weight of water = rho*g
        price_per_mcm = price_per_kWh * gamma * head * eta * 24 / 1e6

        # We can add some conversion function here to go from price to Pywr cost
        # For now, divide by 100, which results in costs of about -5 to -170
        # E-flow costs can be set to less than this, or say -1000
        cost = - price_per_mcm / 100
        return cost

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


network_PH_Cost.register()

print(" [*] PH_Cost successfully registered")
