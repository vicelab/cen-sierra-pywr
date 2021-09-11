import numpy as np
from sierra.base_parameters import BaseParameter
from datetime import datetime
from sierra.utilities.converter import convert


class Kirkwood_PH_Demand(BaseParameter):
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

        # HH storage
        month_day = (timestep.month, timestep.day)
        end_month = 7
        end_day = 15
        if (2, 1) <= month_day <= (end_month, end_day):
            start = timestep.datetime
            end = datetime(timestep.year, end_month, end_day)
            forecast_days = (end - start).days + 1
            forecast_HH_inflow = self.model.parameters["Hetch Hetchy Reservoir Inflow/Runoff"].dataframe[start:end].sum()
            HH = self.model.nodes["Hetch Hetchy Reservoir"]
            current_storage_mcm = HH.volume[scenario_index.global_id]
            HH_space = HH.max_volume - current_storage_mcm
            forecast_spill = forecast_HH_inflow - HH_space
            if forecast_spill > 0:
                release_cms = forecast_spill / forecast_days / 0.0864
                # release_cms = 20
                # release_cms = self.model.nodes["Kirkwood PH"].max_flow / 0.0864

        demand_reduction = self.model.parameters["SFPUC requirement/Demand Reduction"].get_value(scenario_index)

        # TODO: the following is in conflict with SJPL demand, which *increases* during demand reduction periods
        release_cms *= (1 - demand_reduction)

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


Kirkwood_PH_Demand.register()
