from parameters import WaterLPParameter
import numpy as np
from utilities.converter import convert


class SFPUC_requirement_Demand_Reduction(WaterLPParameter):
    """"""

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.demand_reduction = np.zeros(num_scenarios)

    def _value(self, timestep, scenario_index):
        sid = scenario_index.global_id

        if (timestep.month, timestep.day) == (7, 1):

            annual_demand_mcm = 426.22

            total_storage = 0.0
            for res in ['Hetch Hetchy Reservoir', 'Cherry Lake', 'Lake Eleanor']:
                total_storage += self.model.nodes[res].volume[sid]
            total_storage += self.model.parameters["Don Pedro Water Bank"].value(timestep, scenario_index)

            years_supply_remaining = total_storage / annual_demand_mcm

            if years_supply_remaining >= 3.0:
                demand_reduction = 0.0
            elif years_supply_remaining >= 2.5:
                demand_reduction = 0.1
            elif years_supply_remaining >= 2.0:
                demand_reduction = 0.2
            else:
                demand_reduction = 0.25
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
print(" [*] SFPUC_requirement_Demand_Reduction successfully registered")
