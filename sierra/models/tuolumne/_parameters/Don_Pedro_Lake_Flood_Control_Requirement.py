from datetime import datetime
from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Don_Pedro_Lake_Flood_Control_Requirement(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.model.mode == 'planning':
            return 0

        month = timestep.month
        day = timestep.day
        month_day = (month, day)

        # Get target storage
        flood_curve = self.model.tables["Don Pedro Lake Flood Control Curve"]
        flood_control_curve_mcm = flood_curve.at['{}-{}'.format(month, day)]

        NDP = self.model.nodes["Don Pedro Reservoir"]

        # Get previous storage
        prev_storage_mcm = NDP.volume[scenario_index.global_id]

        # Normal release
        MID_mcm = self.model.parameters["Modesto Irrigation District/Demand"].get_value(scenario_index)
        TID_mcm = self.model.parameters["Turlock Irrigation District/Demand"].get_value(scenario_index)
        IFR_mcm = self.model.parameters["IFR at La Grange/Min Flow"].get_value(scenario_index)
        release_mcm = MID_mcm + TID_mcm + IFR_mcm
        if prev_storage_mcm - release_mcm >= flood_control_curve_mcm:
            release_mcm += prev_storage_mcm - release_mcm - flood_control_curve_mcm

        # Refill release to prevent uncontrolled spill before July 1
        end_month = 7
        end_day = 1
        FNF_df = self.model.parameters["Full Natural Flow"].dataframe
        start = timestep.datetime
        DP_flood_control = self.model.nodes["Don Pedro Lake Flood Control"]
        if (4, 1) <= month_day <= (end_month, end_day):
            end = datetime(timestep.year, end_month, end_day)
            forecast_days = (end - start).days + 1
            forecast_all = FNF_df[start:end].sum()
            forecast_above_HH = self.model.parameters["Hetch Hetchy Reservoir Inflow/Runoff"].dataframe[start:end].sum()
            SFPUC_diversion = 920 / 35.315 * 0.0864 * forecast_days
            forecast = forecast_all - forecast_above_HH + max(forecast_above_HH - SFPUC_diversion, 0.0)

            NDP_space = NDP.max_volume - prev_storage_mcm - 20 * 1.2335
            HH = self.model.nodes["Hetch Hetchy Reservoir"]
            HH_space = HH.max_volume - HH.volume[scenario_index.global_id]
            available_space = NDP_space + HH_space
            forecasted_spill = forecast - available_space  # 20 TAF buffer
            if forecasted_spill > 0:
                release_mcm = max(release_mcm, forecasted_spill / forecast_days)

                # limit extra release 4000 cfs (9.7862 mcm) if we are below the flood curve
                # if prev_storage_mcm < flood_control_curve_mcm:
                #     release_mcm = min(release_mcm, 9.7862)

        if (7, 1) < month_day <= (10, 7):
            end = datetime(timestep.year, 10, 7)
            drawdown_days = (end - start).days + 1
            # oct_target_mcm = 1690 cfs w/ 10 cfs buffer = (1690 - 10) * 1.2335 = 2072.28 mcm
            drawdown_release_mcm = max((prev_storage_mcm - 2072.28) / drawdown_days, 0)
            inflow_forecast_mcm = FNF_df[start:end].sum() / drawdown_days
            # downstream_demand_mcm = MID_mcm + TID_mcm + IFR_mcm
            downstream_demand_mcm = 3
            extra_release_mcm = max(drawdown_release_mcm + inflow_forecast_mcm - downstream_demand_mcm, 0)
            release_mcm += extra_release_mcm

            # Let's also limit ramping (for both instream flow and reservoir management reasons)
            prev_release_mcm = DP_flood_control.prev_flow[scenario_index.global_id]
            if release_mcm > prev_release_mcm:
                release_mcm = min(release_mcm, prev_release_mcm * 0.99)
            elif release_mcm < prev_release_mcm:
                release_mcm = max(release_mcm, prev_release_mcm * 0.9)

        max_release_mcm = MID_mcm + TID_mcm + 9000 / 35.31 * 0.0864

        release_mcm = min(release_mcm, max_release_mcm)  # max release

        return release_mcm / 0.0864

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


Don_Pedro_Lake_Flood_Control_Requirement.register()
