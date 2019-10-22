from parameters import WaterLPParameter


class network_PH_Cost(WaterLPParameter):
    """"""

    # path = "s3_imports/energy_netDemand.csv"

    baseline_median_daily_energy_demand = 768  # 768 GWh is median daily energy demand for 2009

    def _value(self, timestep, scenario_index, mode='scheduling'):

        totDemandP = self.model.parameters["Total Net Energy Demand"].dataframe
        maxDemandP = self.model.parameters["Max Net Energy Demand"].dataframe
        minDemandP = self.model.parameters["Min Net Energy Demand"].dataframe

        days_in_period = 1

        if self.mode == 'scheduling':
            totDemand = totDemandP.value(timestep, scenario_index)
            minDemand = maxDemandP.value(timestep, scenario_index)
            maxDemand = maxDemandP.value(timestep, scenario_index)

        else:
            dates_in_period = self.dates_in_month(self.year, self.month)
            days_in_period = len(dates_in_period)
            totDemand = totDemandP[dates_in_period].sum()
            minDemand = minDemandP[dates_in_period].min()
            maxDemand = maxDemandP[dates_in_period].max()

        minVal = self.model.parameters[self.demand_constant_param].value(timestep, scenario_index) \
                 * (totDemand / (self.baseline_median_daily_energy_demand * days_in_period))
        maxVal = minVal * (maxDemand / minDemand)
        d = maxVal - minVal

        nblocks = self.model.parameters['Blocks'].value(timestep, scenario_index)
        return -(maxVal - ((self.block * 2 - 1) * d / 2) / nblocks)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index, mode=self.mode)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


network_PH_Cost.register()

print(" [*] PH_Cost successfully registered")
