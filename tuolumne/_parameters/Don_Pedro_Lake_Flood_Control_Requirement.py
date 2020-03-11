from datetime import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class Don_Pedro_Lake_Flood_Control_Requirement(WaterLPParameter):
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
        MID_mcm = self.model.parameters["Modesto Irrigation District/Demand"].value(timestep, scenario_index)
        TID_mcm = self.model.parameters["Turlock Irrigation District/Demand"].value(timestep, scenario_index)
        IFR_mcm = self.model.parameters["IFR bl La Grange Reservoir/Min Flow"].value(timestep, scenario_index)
        release_mcm = MID_mcm + TID_mcm + IFR_mcm
        if prev_storage_mcm - release_mcm >= flood_control_curve_mcm:
            release_mcm += prev_storage_mcm - release_mcm - flood_control_curve_mcm

        # Refill release to prevent uncontrolled spill before July 1
        end_month = 7
        end_day = 1
        FNF = self.model.tables["Full Natural Flow"]
        start = timestep.datetime
        DP_flood_control = self.model.nodes["Don Pedro Lake Flood Control"]
        if (4, 1) <= month_day <= (end_month, end_day):
            end = datetime(timestep.year, end_month, end_day)
            forecast = FNF[start:end].sum()
            available_space = NDP.max_volume - prev_storage_mcm
            forecasted_spill = forecast - (available_space - 20 * 1.2335)  # 20 TAF buffer
            if forecasted_spill > 0:
                forecast_days = (end - start).days + 1
                release_mcm = max(release_mcm, forecasted_spill / forecast_days)

        if (7, 1) < month_day <= (10, 7):
            end = datetime(timestep.year, 10, 7)
            drawdown_days = (end - start).days + 1
            prev_release_mcm = DP_flood_control.prev_flow[scenario_index.global_id]
            oct_target_mcm = (1690 - 10) * 1.2335
            seasonal_drawdown_mcm = prev_storage_mcm - oct_target_mcm
            drawdown_release_mcm = max(seasonal_drawdown_mcm / drawdown_days, 0)
            extra_release_mcm = max(drawdown_release_mcm + FNF[start] - MID_mcm - TID_mcm - IFR_mcm, 0)
            release_mcm += extra_release_mcm

            # Let's also limit ramping (for both instream flow and reservoir management reasons)
            if release_mcm > prev_release_mcm:
                release_mcm = min(release_mcm, prev_release_mcm * 1.1)
            elif release_mcm < prev_release_mcm:
                release_mcm = max(release_mcm, prev_release_mcm * 0.9)

        max_release_mcm = MID_mcm + TID_mcm + IFR_mcm + 8000 / 35.31 * 0.0864

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
print(" [*] Don_Pedro_Lake_Flood_Control_Requirement successfully registered")
