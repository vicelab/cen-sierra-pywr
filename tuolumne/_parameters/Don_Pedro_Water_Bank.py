import numpy as np
from parameters import WaterLPParameter


class Don_Pedro_Water_Bank(WaterLPParameter):

    initial_storage = None

    def setup(self):
        super().setup()
        # allocate an array to hold the previous storage; will be overwritten each timestep
        num_scenarios = len(self.model.scenarios.combinations)
        self.initial_storage = np.empty([num_scenarios], np.float64)

    def _value(self, timestep, scenario_index):

        if timestep.index == 0:
            initial_storage = 400 * 1.2335  # 400 TAF initial storage
            self.initial_storage[scenario_index.global_id] = initial_storage
            return initial_storage

        inflow = self.model.nodes["TUO_01 Inflow"].prev_flow[scenario_index.global_id]
        outflow = self.model.parameters["Districts Entitlements"].value(timestep, scenario_index)
        initial_storage = self.initial_storage[scenario_index.global_id]
        # initial_storage = self.model.recorders["Don Pedro Water Bank"][timestep.index, scenario_index.global_id]
        new_storage = max(min(initial_storage + inflow - outflow, 703.1), 0.0)

        self.initial_storage[scenario_index.global_id] = new_storage

        return new_storage

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


Don_Pedro_Water_Bank.register()
print(" [*] Don_Pedro_Water_Bank successfully registered")
