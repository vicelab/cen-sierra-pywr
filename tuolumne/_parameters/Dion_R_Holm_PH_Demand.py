import numpy as np
from parameters import WaterLPParameter

from utilities.converter import convert


class Dion_R_Holm_PH_Demand(WaterLPParameter):
    """"""

    prev_release_cms = None

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.prev_release_cms = np.zeros(num_scenarios, np.float)

    def _value(self, timestep, scenario_index):

        if timestep.index % 7 != 0:
            return self.prev_release_cms[scenario_index.global_id]

        release_cms = 0.0

        # Cherry storage
        cherry_storage_mcm = self.model.nodes["Cherry Lake"].volume[scenario_index.global_id]

        # Water Bank storage
        water_bank_storage = self.model.parameters["Don Pedro Water Bank"].value(timestep, scenario_index)
        water_bank_storage_curve = self.model.parameters["Water Bank Preferred Storage AF"] \
                                       .value(timestep, scenario_index) / 1000 * 1.2335

        # Cherry storage min threshold = 100 * 1.2335 = 123.5
        if cherry_storage_mcm >= 185 and water_bank_storage < water_bank_storage_curve:
            # release_cms = 1.924 taf/day * 1.2335 mcm/taf / 0.0864 = 27.47
            release_cms = 27.47 / 3

        self.prev_release_cms[scenario_index.global_id] = release_cms

        return release_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
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


Dion_R_Holm_PH_Demand.register()
print(" [*] Dion_R_Holm_Tunnel_Flow_Capacity successfully registered")
