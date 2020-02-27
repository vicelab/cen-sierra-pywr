from datetime import datetime, timedelta
from parameters import WaterLPParameter

from utilities.converter import convert


class New_Melones_Flood_Control_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # For the planning model, we don't care about reservoir volume, at least for now
        # In the future, we might, since ag. diversions could depend on storage.
        # Note that this linear, time step dependent approach only works for the scheduling model,
        # note the planning model, since planning model time steps are not sequentially determined.
        # Instead, a piecewise reservoir approach will need to be applied.
        # TODO: revisit the above rationale for not including flood control in the planning model.
        if self.model.mode == 'planning':
            return 0

        # Flood control has 2 components, based on USACE manuals:
        # 1. Flood control space
        # 2. Conditional space

        # In addition to flood control, we will also release at a steady rate if we fill, down to some target storage
        # before we hit the flood control space again in Oct. This is to spread drawdown over a longter period of time,
        # based on observations

        month = self.datetime.month
        day = self.datetime.day
        start_tuple = (month, day)

        # Get expected ag. releases, so we can release more if needed
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        SSJID_df = self.model.tables["South San Joaquin Irrigation District Demand"][WYT]
        OID_df = self.model.tables["Oakdale Irrigation District Demand"][WYT]

        # 1. Flood control space operations

        # Get target storage
        month_day = '{}-{}'.format(month, day)
        flood_curves = self.model.tables["New Melones Lake Flood Control"]

        # Get previous storage
        NML = self.model.nodes["New Melones Lake"]
        prev_storage_mcm = NML.volume[scenario_index.global_id]

        # Today's release volume, just based on flooding
        # This only looks back one day. Although it doesn't anticipate inflows, it does account for ag. diversions
        # inflow_mcm = self.model.tables["Full Natural Flow"][self.datetime]
        # release_mcm = prev_storage_mcm + inflow_mcm - ag_demand_mcm - max_storage_mcm

        flood_control_curve_mcm = flood_curves.at[month_day, 'flood control space']
        conditional_curve_mcm = flood_curves.at[month_day, 'conditional space']

        release_mcm = 0.0

        ag_demand_mcm = SSJID_df[start_tuple] + OID_df[start_tuple]

        if prev_storage_mcm >= flood_control_curve_mcm:
            # 1. flood control operations we are in the flood control space
            release_mcm = prev_storage_mcm - flood_control_curve_mcm

        # 2. Conditional space operations
        elif prev_storage_mcm >= conditional_curve_mcm:

            forecast_days = 7
            forecast_date = self.datetime + timedelta(days=forecast_days)
            end_month_day = '{}-{}'.format(forecast_date.month, forecast_date.day)

            # forecasted target
            forecasted_target_storage_mcm = flood_curves.at[end_month_day, 'flood control space']

            # Get expected FNF inflow
            forecasted_inflow_mcm = self.model.tables["Full Natural Flow"][self.datetime:forecast_date].sum()

            # Forecasted release volume
            release_mcm \
                = prev_storage_mcm \
                  + forecasted_inflow_mcm \
                  - forecasted_target_storage_mcm

            # divide by forecast days to get the release today (will spread this out over time)
            release_mcm /= forecast_days

            # Forecasted ag demand
            # end_tuple = (forecast_date.month, forecast_date.day)
            # SSJID_mcm = SSJID_df[start_tuple:end_tuple].sum()
            # OID_mcm = OID_df[start_tuple:end_tuple].sum()
            # ag_demand_mcm = SSJID_mcm + OID_mcm

            # divide by forecast_days to spread out over time
            # ag_demand_mcm /= forecast_days

        # This is our overall target release, without accounting for max downstream releases
        release_mcm = float(max(release_mcm, 0))

        # ...however, this should be reduced as needed to limit flow Orange Blossom Bridge to <= 8000 cfs
        # 8000 cfs =
        orange_blossom_bridge_max_mcm = 8000 / 35.31 * 0.0864
        max_release_mcm = ag_demand_mcm + orange_blossom_bridge_max_mcm

        release_mcm = min(release_mcm, max_release_mcm)

        # Let's also release extra if the reservoir filled and release slowly to a target storage of 1970 TAF (2430 MCM)
        # by Oct 31. This is based on observation, though need to confirm

        nov1_target = 2430

        drawdown_period = (7, 1) <= start_tuple <= (10, 31)
        if timestep.index == 0:
            self.should_drawdown = True
        elif not drawdown_period:
            self.should_drawdown = False

        # Stop this if we've hit the target
        if prev_storage_mcm < nov1_target:
            self.should_drawdown = False

        # # Check if New Melones filled
        if drawdown_period and prev_storage_mcm > nov1_target and not self.should_drawdown:
            day_before_yesterday = self.datetime + timedelta(days=-2)
            prev_prev_storage_mcm = self.model.recorders["New Melones Lake/storage"]\
                .to_dataframe().at[day_before_yesterday, tuple(scenario_index.indices)]
            if prev_storage_mcm - prev_prev_storage_mcm <= 0:
                self.should_drawdown = True

        if drawdown_period and self.should_drawdown:
            drawdown_release_mcm = (prev_storage_mcm - nov1_target) \
                                   / (datetime(timestep.year, 11, 1) - timestep.datetime).days * 1.2335
            prev_inflow_mcm = self.model.nodes["STN_01 Inflow"].prev_flow[scenario_index.global_id]

            drawdown_release_mcm += prev_inflow_mcm

            # Note: This may result in a high up ramp rate in late summer. This should be accounted for
            # in the relevant IFR (i.e. below Goodwin Dam), not here.
            release_mcm = max(release_mcm, drawdown_release_mcm)

        release_cms = release_mcm / 0.0864

        return release_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Flood_Control_Requirement.register()
print(" [*] New_Melones_Flood_Control_Requirement successfully registered")
