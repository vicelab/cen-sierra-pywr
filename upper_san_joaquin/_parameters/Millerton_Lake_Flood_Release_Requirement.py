from parameters import WaterLPParameter
from datetime import datetime, timedelta
import numpy as np
from utilities.converter import convert
import datetime as dt
import math


class Millerton_Lake_Flood_Release_Requirement(WaterLPParameter):

    should_drawdown = None

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.should_drawdown = np.empty(num_scenarios, np.bool)

    def _value(self, timestep, scenario_index):

        if self.model.mode == 'planning':
            return 0

        # Note: the following logic follows the U.S. Army Corps of Engineers 1980 Water Control Manual for Friant Dam

        month = self.datetime.month
        day = self.datetime.day
        month_day = '{}-{}'.format(month, day)

        # Get flood curve
        flood_curves = self.model.tables["Millerton Lake flood curve"]
        rainflood_curve_mcm = flood_curves.at[month_day, 'rainflood']
        conditional_curve_mcm = flood_curves.at[month_day, 'conditional']

        # Get previous storage
        NML = self.model.nodes["Millerton Lake"]
        millerton_storage_mcm = NML.volume[scenario_index.global_id]

        # Load base ag demand info
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        Madera_df = self.model.tables["CVP Madera Canal demand"][WYT]
        Friant_Kern_df = self.model.tables["CVP Friant-Kern Canal demand"][WYT]

        # Set the default release of zero
        release_mcm = 0.0

        # 1. Conservation space release
        if millerton_storage_mcm < conditional_curve_mcm:
            pass

        # 2. Rainflood space release
        max_storage = NML.get_max_volume(scenario_index)
        above_85_taf_mcm = max_storage - rainflood_curve_mcm - 104.85
        if above_85_taf_mcm > 0.0 and (month >= 10 or month <= 3):  # 85 TAF
            mammoth_pool_mcm = self.model.nodes["Mammoth Pool Reservoir"].volume[scenario_index.global_id]
            rainflood_curve_mcm += min(above_85_taf_mcm, mammoth_pool_mcm)

        elif millerton_storage_mcm >= rainflood_curve_mcm:
            release_mcm = millerton_storage_mcm - rainflood_curve_mcm

        # 3. Conditional space release
        elif 2 <= month <= 7:
            # Note: Here, we are calculating forecasts directly as able, rather than using the USACE manual diagram.

            # 3.1. Calculate forecasted unimpaired runoff into Millerton Lake, through July 31.
            # For now, assume perfect forecast.
            # TODO: update to use imperfect forecast?
            fnf_start = timestep.datetime
            fnf_end = datetime(timestep.year, 7, 31)
            forecasted_inflow_mcm = self.model.tables["Full Natural Flow"][fnf_start:fnf_end].sum()

            # 3.2. Calculate today's and forecasted irrigation demand.
            ag_start = (month, day)
            if (month, day) <= (5, 31):
                ag_end = (6, 15)
            else:
                # min of +15 days (1-15 = today + 14 days)
                ag_end_date = timestep.datetime + timedelta(days=14)
                ag_end = min((ag_end_date.month, ag_end_date.day), (8, 1))

            # today_ag_demand = Madera_df[ag_start] + Friant_Kern_df[ag_start]
            forecasted_ag_demand_cfs = Madera_df[ag_start:ag_end].sum() + Friant_Kern_df[ag_start:ag_end].sum()
            forecasted_ag_demand_mcm = forecasted_ag_demand_cfs / 35.31 * 0.0864

            # 3.3. Calculate total space required for flood control
            # slope from flood control chart = 1 / 1.6
            total_space_required_mcm = forecasted_inflow_mcm * 0.625 - forecasted_ag_demand_mcm

            # 3.4. Calculate upstream space, adjusted

            # 3.4.1. Get total previous storage in upstream reservoirs
            upstream_storage_space_mcm = 0.0
            for node in self.model.nodes:
                # TODO: make this more efficient
                if hasattr(node, 'volume') and node.name != 'Millerton Lake':
                    upstream_storage_space_mcm += node.volume[scenario_index.global_id]

            # 3.4.2. Calculate adjustment to storage space
            # Note: this is approximated from the upper right of the Flood Control Diagram (Fig. A-11)
            days_since_feb1 = (timestep.datetime - datetime(timestep.year, 2, 1)).days
            adjustment_to_upstream_space_taf = 100 - 3.1623e-9 * math.exp(0.13284 * days_since_feb1)
            adjustment_to_upstream_space_mcm = adjustment_to_upstream_space_taf * 1.2335

            # 3.4.3. Subtract adjustment from upstream space
            adjusted_upstream_storage_space_mcm = upstream_storage_space_mcm - adjustment_to_upstream_space_mcm

            # 3.5. Calculate conditional reservation required
            # Note: It does not appear that this is actually used in the Flood Control Diagram
            conditional_space_required_mcm = total_space_required_mcm - adjusted_upstream_storage_space_mcm

            # 3.6. Compute total space available for flood control
            total_space_available_mcm = millerton_storage_mcm + upstream_storage_space_mcm \
                                        - adjustment_to_upstream_space_mcm

            # 3.7. Finally, compute the supplemental release
            # Note that the goal is to spread the release out over time
            # storage_difference_mcm = max(total_space_required_mcm - total_space_available_mcm, 0.0)

            # if storage_difference_mcm > 0.0:
            #     print('{}: conditional; release: {} taf'.format(timestep.datetime, storage_difference_mcm / 1.2335))

            # if (month, day) <= (5, 5):
            #
            #
            # elif (month, day) <= (6, 5):
            #
            #
            # elif (month, day) <= (6, 30):
            #
            #
            # else:

            supplemental_release_mcm = conditional_space_required_mcm - millerton_storage_mcm

            days_until_jul31 = (datetime(timestep.year, 7, 31) - timestep.datetime).days + 1
            supplemental_release_mcm /= days_until_jul31

            # 3.8. Calculate total release
            # Note that this differs from the example in the USACE manual, since we are only calculating instream
            # release here. In the manual, "total release" is instream release + ag. release
            release_mcm = supplemental_release_mcm

        # This is our overall target release, without accounting for max downstream releases
        release_mcm = float(max(release_mcm, 0.0))

        # Assume Madera Canal can absorb some flood control capacity
        # Note that we cannot calculate Madera demand from the demand node/parameter, since that node depends on this.
        if release_mcm > 0.0:
            madera_canal_cfs = Madera_df[(month, day)]
            madera_canal_mcm = madera_canal_cfs / 35.315 * 0.0864
            madera_canal_max_mcm = self.model.nodes["Madera Canal.1"].max_flow
            adjusted_release_mcm = release_mcm - (madera_canal_max_mcm - madera_canal_mcm)
            release_mcm = max(adjusted_release_mcm, 0.0)

        # ...reduce to limit flow to <= 8000 cfs (19.57 mcm)
        little_dry_creek_max_mcm = 19.57
        release_mcm = min(release_mcm, little_dry_creek_max_mcm)

        # DRAWDOWN OPERATIONS

        # Release slowly to a target storage of 350 TAF by Oct 31.

        if (7, 1) <= (month, day) <= (10, 31):
            sid = scenario_index.global_id
            nov1_target = 431.725  # 350 TAF

            # Stop this if we've hit the target
            if millerton_storage_mcm < nov1_target:
                self.should_drawdown[sid] = False

            # Check if New Melones filled
            if millerton_storage_mcm > nov1_target and not self.should_drawdown[sid]:
                day_before_yesterday = self.datetime + timedelta(days=-2)
                prev_millerton_storage_mcm = self.model.recorders["Millerton Lake/storage"] \
                    .to_dataframe().at[day_before_yesterday, tuple(scenario_index.indices)]
                if millerton_storage_mcm - prev_millerton_storage_mcm <= 0:
                    self.should_drawdown[sid] = True

            if self.should_drawdown[sid]:
                drawdown_release_mcm = (millerton_storage_mcm - nov1_target) \
                                       / (datetime(timestep.year, 11, 1) - timestep.datetime).days
                prev_inflow_mcm = 0.0
                for node in ['Kerckhoff 1 PH', 'Kerckhoff 2 PH', 'IFR bl Kerckhoff Lake', 'Millerton Lake Inflow']:
                    prev_inflow_mcm += self.model.nodes[node].prev_flow[scenario_index.global_id]

                drawdown_release_mcm += prev_inflow_mcm

                release_mcm = max(release_mcm, drawdown_release_mcm)

                # Let's also limit ramping (for both instream flow and reservoir management reasons)
                prev_release_mcm = self.model.nodes["Millerton Lake Flood Release"].prev_flow[scenario_index.global_id]
                if release_mcm > prev_release_mcm:
                    release_mcm = min(release_mcm, prev_release_mcm * 1.1)
                elif release_mcm < prev_release_mcm:
                    release_mcm = max(release_mcm, prev_release_mcm * 0.9)

        release_cms = release_mcm / 0.0864

        return release_cms

    def value(self, *args, **kwargs):
        try:
            return convert(self._value(*args, **kwargs), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Millerton_Lake_Flood_Release_Requirement.register()
print(" [*] Millerton_Lake_Flood_Release_Requirement successfully registered")
