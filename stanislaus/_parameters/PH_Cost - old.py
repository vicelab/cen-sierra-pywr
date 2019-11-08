from parameters import WaterLPParameter


class PH_Cost(WaterLPParameter):
    """"""

    # path = "s3_imports/energy_netDemand.csv"

    baseline_median_daily_energy_demand = 768  # 768 GWh is median daily energy demand for 2009

    def _value(self, timestep, scenario_index, mode='scheduling'):

        if timestep.index == 0:
            self.nblocks = self.model.parameters["Blocks"].get_value(scenario_index)
            self.demandParam = self.model.parameters[self.res_name + '/Demand Constant'].get_value(scenario_index)

        totDemandP = self.model.parameters["Total Net Energy Demand"]
        maxDemandP = self.model.parameters["Max Net Energy Demand"]
        minDemandP = self.model.parameters["Min Net Energy Demand"]

        if self.mode == 'scheduling':
            days_in_period = 1
            totDemand = totDemandP.value(timestep, scenario_index)
            minDemand = maxDemandP.value(timestep, scenario_index)
            maxDemand = maxDemandP.value(timestep, scenario_index)

        else:
            planning_dates = self.dates_in_month()
            days_in_period = len(planning_dates)
            totDemand = totDemandP.dataframe[planning_dates].sum()
            minDemand = minDemandP.dataframe[planning_dates].min()
            maxDemand = maxDemandP.dataframe[planning_dates].max()

        baselineDemand = self.baseline_median_daily_energy_demand * days_in_period
        minVal = self.demandParam * (totDemand / baselineDemand)
        maxVal = minVal * (maxDemand / minDemand)
        max_min_diff = maxVal - minVal

        value = maxVal - ((max_min_diff / (2 * self.nblocks)) * (self.block * 2 - 1))
        return -value

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index, mode=self.mode)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


PH_Cost.register()

print(" [*] PH_Cost successfully registered")
