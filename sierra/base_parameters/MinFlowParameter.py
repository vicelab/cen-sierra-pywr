import random
from dateutil.relativedelta import relativedelta

from sierra.base_parameters import IFRParameter


class FlowPeriods(object):
    DRY_SEASON = 'dry season'
    FALL_PULSE = 'fall pulse'
    WET_SEASON = 'wet season'
    SPRING_RECESSION = 'spring recession'


class MinFlowParameter(IFRParameter):
    current_flow_period = None
    water_year_type = None
    params = None
    dowy = None

    # Functional flows parameters
    magnitude_col = None
    dry_season_baseflow_mcm = None
    include_functional_flows = False
    wet_baseflow_start = 100
    spring_recession_start = 250
    flood_lengths = {2: 7, 5: 2, 10: 2}

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        for s in self.model.scenarios.scenarios:
            if 'Functional Flows' in s.ensemble_names:
                self.current_flow_period = [FlowPeriods.DRY_SEASON] * self.num_scenarios

                self.include_functional_flows = True
                self.metrics = self.model.tables['functional flows metrics']
                self.water_year_type = 'moderate'
                self.close_wet_season_gates = False

                self.water_year_types = {
                    1: 'dry',
                    2: 'moderate',
                    3: 'wet'
                }

                self.prev_requirement = [0] * self.num_scenarios
                self.flood_days = [0] * self.num_scenarios
                self.flood_duration = [0] * self.num_scenarios
                self.prev_flood_mcm = [0] * self.num_scenarios
                self.flood_year = [0] * self.num_scenarios

                # 2-year flood: 18670 cfs x 7 days = 320 mcm flood total
                # 5-year flood: 40760 cfs x 2 days = 199 mcm flood total
                # 10-year flood: 52940 cfs x 2 days = 259 mcm flood total
                # floods = self.model.tables['functional flows floods']
                # self.flood_lengths = flood_lengths = {10: 2, 5: 2, 2: 7}  # these should be from highest to lowest
                # self.flood_volumes_mcm = {}
                # for return_interval in flood_lengths:
                #     self.flood_volumes_mcm[return_interval] \
                #         = floods['{}-year'.format(return_interval)] / 35.315 * 0.0864 * flood_lengths[return_interval]

    def before(self):
        super().before()

        timestep = self.model.timestep

        if timestep.month >= 10:
            dowy = timestep.dayofyear - 275 + 1
        else:
            dowy = timestep.dayofyear + 92 - 1
        self.dowy = dowy

        if self.include_functional_flows:

            if timestep.month == 10 and timestep.day == 1:
                # update water year type, assuming perfect foresight
                wy = timestep.year + 1
                fnf_annual = self.model.tables['Annual Full Natural Flow']
                terciles = fnf_annual.quantile([0, 0.33, 0.66]).values
                wyt = sum([1 for q in terciles if fnf_annual[wy] >= q])
                self.water_year_type = self.water_year_types[wyt]
                self.close_wet_season_gates = True

    def get_down_ramp_ifr(self, timestep, scenario_index, value, initial_value=None, rate=0.25):
        """

        :param timestep:
        :param scenario_index:
        :param value: cubic meters per second
        :param initial_value: cubic meters per second
        :param rate:
        :return:
        """
        if timestep.index == 0:
            if initial_value is not None:
                Qp = initial_value
            else:
                Qp = value
        else:
            Qp = self.model.nodes[self.res_name].prev_flow[scenario_index.global_id] / 0.0864  # convert to cms
        return max(value, Qp * (1 - rate))

    def requirement(self, timestep, scenario_index, default=None):
        """
        Calculate a custom IFR other than the baseline IFR
        :param timestep:
        :param scenario_index:
        :return:
        """

        if self.ifrs_idx is not None:
            scenario_name = self.ifr_names[scenario_index.indices[self.ifrs_idx]]
        else:
            scenario_name = None

        min_flow_mcm = 0.0

        if scenario_name == 'No IFRs':
            min_flow_mcm = 0.0

        elif scenario_name == 'SWRCB' and self.ifr_type == 'enhanced':
            min_flow_mcm = self.swrcb_flows_min_flow(timestep, scenario_index)

        elif scenario_name == 'Functional Flows' and self.ifr_type == 'enhanced':
            if self.model.mode == 'scheduling':
                min_flow_mcm = self.functional_flows_min_flow_scheduling(timestep, scenario_index, scenario_name)
            else:
                min_flow_mcm = self.functional_flows_min_flow_planning(timestep, scenario_index, scenario_name)

        elif default:
            min_flow_mcm = default(timestep, scenario_index)

        return min_flow_mcm

    def swrcb_flows_min_flow(self, timestep, scenario_index):
        fnf_mcm = self.model.parameters['Full Natural Flow'].get_value(scenario_index)
        ifr_mcm = fnf_mcm * 0.4
        ifr_cms = ifr_mcm / 0.0864
        return ifr_cms

    def functional_flows_min_flow_scheduling(self, timestep, scenario_index, scenario_name=None):
        """
        Calculate the minimum functional flow
        :param timestep:
        :param scenario_index:
        :return:
        """
        sid = scenario_index.global_id

        metrics = self.metrics[self.water_year_type]

        ifr_mcm = 0.0
        ifr_cfs = 0.0
        fnf = self.model.parameters['Full Natural Flow'].dataframe

        # Dry season baseflow
        if self.dowy < metrics['Wet_Tim']:

            if metrics['FA_Tim'] <= self.dowy <= metrics['FA_Tim'] + metrics['FA_Dur'] - 1:
                ifr_cfs = metrics['FA_Mag']

            else:
                ifr_cfs = metrics['DS_Mag_50']

        # Low wet season baseflow
        elif self.dowy < metrics['SP_Tim']:
            # TODO: change logic as follows (FIRST 3 LINES ARE OBSOLETE)
            # 1. Start by releasing all inflow
            # 2. If a 2-year flood has passed (i.e., look back 7 days), then drop to the 10th percentile base flow
            # 3. Look forward 2-7 days and release incoming 2, 5, or 10 year event

            # 1. Look forward 1 day and release incoming event at a magnitude less than or equal to the next lower
            # associated frequency
            # For example, if a 15-year event is seen, release a 10-year peak (Peak_10)
            # If tomorrow's magnitude is between a 5 & 10 year event, release at the 5-year event level

            fnf_cfs = fnf[timestep.datetime] / 0.0864 * 35.315  # fnf mcm -> cfs
            ifr_cfs = metrics['Wet_BFL_Mag_10']
            for peak_freq in [10, 5, 2]:
                peak_cfs = metrics['Peak_{}'.format(peak_freq)]
                if fnf_cfs >= peak_cfs:
                    ifr_cfs = peak_cfs
                    break

        # Spring recession
        elif self.dowy == metrics['SP_Tim']:
            ifr_cfs = metrics['SP_Mag']

        # ...ramp down
        else:
            ramp_rate = 0.07
            prev_flow_mcm = self.model.nodes[self.res_name].prev_flow[sid]
            ifr_cfs = prev_flow_mcm * (1 - ramp_rate) / 0.0864 * 35.315
            # TODO: double check this logic for the end
            ifr_cfs = max(ifr_cfs, metrics['DS_Mag_50'])

        # winter flood season rules
        # winter_flood_mcm = 0
        # winter_flood_cfs = 0
        # winter_flood_season = metrics['Wet_Tim'] <= self.dowy < metrics['SP_Tim']
        #
        # if winter_flood_season or self.prev_flood_mcm[sid]:
        #
        #     if self.flood_days[sid] < self.flood_duration[sid]:
        #         winter_flood_mcm = self.prev_flood_mcm[sid]  # TODO: make scenario-safe
        #
        #     elif self.water_year_type == 'moderate':
        #         flood_start = metrics['Peak_Tim_2']
        #         if self.dowy == flood_start:
        #             self.flood_duration[sid] = metrics['Peak_Dur_2']
        #             winter_flood_cfs = metrics['Peak_2']
        #
        #     elif self.water_year_type == 'wet':
        #         flood_starts = {}
        #         for interval in [2, 5, 10]:
        #             peak_timing = metrics['Peak_Tim_{}'.format(interval)]
        #             flood_starts[peak_timing] = interval
        #             if interval == 2:
        #                 # add in additional 2-year floods
        #                 for i in range(metrics['Peak_Fre_2']):
        #                     flood_starts[peak_timing + 30 * (i - 1)] = interval
        #         if self.dowy in flood_starts:
        #             return_interval = flood_starts[self.dowy]
        #             self.flood_duration[sid] = metrics['Peak_Dur_{}'.format(return_interval)]
        #             winter_flood_cfs = metrics['Peak_{}'.format(return_interval)]
        #
        #     if winter_flood_cfs:
        #         winter_flood_mcm = winter_flood_cfs / 35.315 * 0.0864

            # Old code for hydrology-triggered floods
            # if self.flood_year[sid] and self.flood_days[sid] < self.flood_lengths[self.flood_year[sid]]:
            #     winter_flood_mcm = self.prev_flood_mcm[sid]  # TODO: make scenario-safe
            #
            # else:
            #
            #     forecast_start = timestep.datetime
            #
            #     # loop through return intervals, from highest to lowest
            #     for return_interval, flood_volume_mcm in self.flood_volumes_mcm.items():
            #         days = self.flood_lengths[return_interval]
            #         forecast_mcm = fnf[forecast_start:forecast_start + relativedelta(days=days)].sum()
            #         if forecast_mcm >= flood_volume_mcm:
            #             winter_flood_mcm = flood_volume_mcm / days
            #             self.flood_year[sid] = return_interval
            #             break

            # if winter_flood_mcm:
            #     self.prev_flood_mcm[sid] = winter_flood_mcm
            #     self.flood_days[sid] += 1
            #     # self.num_floods[sid] = min(self.num_floods[sid] + 1, 2)
            # else:
            #     self.prev_flood_mcm[sid] = 0
            #     self.flood_days[sid] = 0
            #     self.flood_duration[sid] = 0
            #     self.flood_year[sid] = 0

        ifr_mcm = ifr_mcm or (ifr_cfs / 35.315 * 0.0864)
        # ifr_mcm = max(ifr_mcm, winter_flood_mcm)

        fnf_mcm = fnf[timestep.datetime]
        ifr_mcm = min(ifr_mcm, fnf_mcm)

        self.prev_requirement[sid] = ifr_mcm

        ifr_cms = ifr_mcm / 0.0864

        return ifr_cms

    def functional_flows_min_flow_planning(self, timestep, scenario_index, scenario_name=None):
        """
        Calculate the minimum functional flow
        :param timestep:
        :param scenario_index:
        :return:
        """

        # TODO: populate this placeholder

        return 0.0
