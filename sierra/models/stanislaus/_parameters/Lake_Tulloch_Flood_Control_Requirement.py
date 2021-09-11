from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Lake_Tulloch_Flood_Control_Requirement(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.model.mode == 'planning':
            return 0

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
        flood_curve = self.model.tables["Lake Tulloch Flood Control"]
        flood_control_curve_mcm = flood_curve.at[month_day] - 1 * 1.2335  # less 1 TAF based on observed

        # Get previous storage
        prev_storage_mcm = self.model.nodes["Lake Tulloch"].volume[scenario_index.global_id]

        release_mcm = 0.0

        ag_demand_mcm = SSJID_df[start_tuple] + OID_df[start_tuple]
        IFR_below_Goodwin_Dam_mcm = self.get("IFR bl Goodwin Reservoir/Min Flow", timestep, scenario_index)

        # start by assuming release is simply a passthrough
        release_mcm = self.get("New Melones Lake Flood Control/Requirement", timestep, scenario_index)

        # 1) increase during the flood period as needed
        if prev_storage_mcm >= flood_control_curve_mcm:
            release_mcm += prev_storage_mcm - flood_control_curve_mcm

        # 2) hold back during the refill period as needed
        if (3, 21) <= start_tuple <= (5, 30):
            if flood_control_curve_mcm > prev_storage_mcm:
                refill_mcm = flood_control_curve_mcm - prev_storage_mcm
                release_mcm = max(release_mcm - refill_mcm, 0)

        # ...however, this should be reduced as needed to limit flow Orange Blossom Bridge to <= 8000 cfs
        # 8000 cfs =
        # orange_blossom_bridge_max_mcm = 8000 / 35.31 * 0.0864
        # max_release_mcm = ag_demand_mcm + orange_blossom_bridge_max_mcm

        # release_mcm = min(release_mcm, max_release_mcm)

        release_cms = release_mcm / 0.0864

        return release_cms

    def value(self, timestep, scenario_index):
        val = self._value(timestep, scenario_index)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Lake_Tulloch_Flood_Control_Requirement.register()
