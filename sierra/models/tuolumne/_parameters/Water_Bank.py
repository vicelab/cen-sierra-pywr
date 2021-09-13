import numpy as np
from sierra.base_parameters import BaseParameter


class Water_Bank(BaseParameter):
    initial_storage = None

    def setup(self):
        super().setup()
        # allocate an array to hold the previous storage; will be overwritten each timestep
        num_scenarios = len(self.model.scenarios.combinations)
        self.initial_storage = np.empty(num_scenarios, np.float64)

    def _value(self, timestep, scenario_index):
        sid = scenario_index.global_id

        if timestep.index == 0:
            initial_storage = 400 * 1.2335  # 400 TAF initial storage
            self.initial_storage[sid] = initial_storage
            return initial_storage

        inflow = self.model.nodes["TUO_01 Inflow"].prev_flow[sid]
        outflow = self.model.parameters["Districts Entitlements"].get_value(scenario_index)
        initial_storage = self.initial_storage[scenario_index.global_id]
        # initial_storage = self.model.recorders["Water Bank"][timestep.index, scenario_index.global_id]

        # calculate total max water bank capacity
        # capacity = 570 TAF (703.1 MCM) + 1/2 unused flood space - 1/2 flood release

        don_pedro_storage = self.model.nodes["Don Pedro Reservoir"].volume[sid]
        # flood_curve = self.model.tables["Don Pedro Lake Flood Control Curve"]
        # flood_control_curve_mcm = flood_curve.at['{}-{}'.format(timestep.month, timestep.day)]

        # unused_space_mcm = max(don_pedro_storage - flood_control_curve_mcm, 0.0)
        unused_space_mcm = max(don_pedro_storage - 2084.58, 0.0)
        prev_flood_release = self.model.parameters["Don Pedro Lake Flood Control/Requirement"].get_value(scenario_index)
        normal_wb_max_mcm = 703.1

        wb_max_mcm = normal_wb_max_mcm + unused_space_mcm / 2 - prev_flood_release / 2

        new_storage = max(min(initial_storage + inflow - outflow, wb_max_mcm), 0.0)

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


Water_Bank.register()
