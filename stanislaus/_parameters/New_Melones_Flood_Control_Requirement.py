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
        if self.model.mode == 'planning':
            return 0

        month = self.datetime.month
        day = self.datetime.day

        if (month, day) == (1, 1) or timestep.index == 0:
            self.NML_did_fill = False

        # get target storage

        forecast_days = 7
        forecast_date = self.datetime + timedelta(days=forecast_days)
        month_day = '{:02}-{:02}'.format(month, day)
        end_month_day = '{:02}-{:02}'.format(forecast_date.month, forecast_date.day)
        target_storage_mcm = self.model.tables["New Melones Lake Flood Control"][month_day]
        forecasted_target_storage_mcm = self.model.tables["New Melones Lake Flood Control"][end_month_day]

        # get previous storage
        NML = self.model.nodes["New Melones Lake"]
        prev_storage_mcm = NML.volume[scenario_index.global_id]
        max_storage = NML.max_volume

        # Check if New Melones filled
        if not self.NML_did_fill and prev_storage_mcm >= max_storage * 0.95:
            self.NML_did_fill = True

        # Get expected inflow; for now, assume FNF
        # TODO: update with subbasin expected inflow less subbasin storage
        forecasted_inflow_mcm = self.model.tables["Full Natural Flow"][self.datetime:forecast_date].sum()
        # forecasted_inflow_mcm *= 1.25

        # Get expected ag. releases, so we can release more if needed
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        SSJID_df = self.model.tables["South San Joaquin Irrigation District Demand"][WYT]
        OID_df = self.model.tables["Oakdale Irrigation District Demand"][WYT]

        start_tuple = (month, day)

        if month == 12 and day + forecast_days > 31:
            days_in_jan = day + forecast_days - 31
            SSJID_mcm = SSJID_df[start_tuple:(12, 31)].sum() + SSJID_df[(1, 1):(1, days_in_jan)].sum()
            OID_mcm = OID_df[start_tuple:(12, 31)].sum() + OID_df[(1, 1):(1, days_in_jan)].sum()
        else:
            end_tuple = (forecast_date.month, forecast_date.day)
            SSJID_mcm = SSJID_df[start_tuple:end_tuple].sum()
            OID_mcm = OID_df[start_tuple:end_tuple].sum()

        forecasted_ag_demand_mcm = SSJID_mcm + OID_mcm

        # Forecasted release volume
        forecasted_release_mcm \
            = prev_storage_mcm \
              + forecasted_inflow_mcm \
              - forecasted_ag_demand_mcm \
              - forecasted_target_storage_mcm

        # Today's release volume, just based on flooding
        ag_demand_mcm = SSJID_df[start_tuple] + OID_df[start_tuple]
        inflow_mcm = self.model.tables["Full Natural Flow"][self.datetime]
        release_mcm = prev_storage_mcm + inflow_mcm - ag_demand_mcm - target_storage_mcm

        over_storage_mcm = float(max(release_mcm, forecasted_release_mcm, 0))

        if 8 <= month <= 11:
            max_release_cfs = 2000
        else:
            max_release_cfs = 8000
        max_release_mcm = max_release_cfs / 35.31 * 0.0864
        release_cms = min(over_storage_mcm, max_release_mcm) / 0.0864

        # Let's also release extra if the reservoir filled and release slowly to a target storage of 2000 TAF by Oct 31.
        # This is based on observation, though need to confirm
        if self.NML_did_fill and (7, 1) <= (month, day) and prev_storage_mcm >= 2000 * 1.2335:
            # reservoir late summer drawdown is ~40.6 cms (350 TAF over Jul-Oct)
            prev_inflow_cms = self.model.nodes["STN_01 Inflow"].prev_flow[scenario_index.global_id] / 0.0864
            release_cms = max(release_cms, 40.6 + prev_inflow_cms)

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
