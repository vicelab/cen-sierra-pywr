from sierra.base_parameters import BaseParameter
import numpy as np


class SFPUC_requirement_Demand_Reduction(BaseParameter):
    """"""

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.demand_reduction = np.zeros(num_scenarios)

    def _value(self, timestep, scenario_index):
        sid = scenario_index.global_id

        if timestep.month in [7] and timestep.day == 1:

            annual_demand_mcm = self.model.parameters["SFPUC requirement/Annual Demand"].value(timestep, scenario_index)

            # calculate total storage, including snowpack
            total_storage = 0.0
            hh = self.model.nodes["Hetch Hetchy Reservoir"].volume[sid]
            ch = self.model.nodes["Cherry Lake"].volume[sid]
            el = self.model.nodes["Lake Eleanor"].volume[sid]
            wb = self.model.parameters["Water Bank"].get_value(scenario_index)

            total_storage = hh + ch + el + wb
            # total_storage = hh + ch + el

            years_supply_remaining = total_storage / annual_demand_mcm

            thresholds = [3.0, 2.8, 2.6]
            # thresholds = [1.8, 1.5, 1.25]
            reductions = [0.0, 0.1, 0.2, 0.25]
            idx = sum([1 for t in thresholds if years_supply_remaining < t])
            demand_reduction = reductions[idx]

            self.demand_reduction[sid] = demand_reduction

        return self.demand_reduction[sid]

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)

        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


SFPUC_requirement_Demand_Reduction.register()
