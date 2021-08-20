import math
import random
from dateutil.relativedelta import relativedelta
from math import log
from datetime import datetime, timedelta
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
    ramp_rate = None
    spring_recession = False

    # Functional flows parameters
    magnitude_col = None
    high_wet_season_baseflow = False
    spring_ramp_up_days = 0.0
    dry_season_baseflow_mcm = None
    include_functional_flows = False
    wet_baseflow_start = 100
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
                self.ramp_up_rate = 0.13

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
                self.water_year = timestep.year + 1
                fnf_annual = self.model.tables['Annual Full Natural Flow']
                terciles = fnf_annual.quantile([0, 0.33, 0.66]).values
                wyt = sum([1 for q in terciles if fnf_annual[self.water_year] >= q])
                self.prev_water_year_type = self.water_year_type
                self.water_year_type = self.water_year_types[wyt]
                self.fall_pulse_released = False
                self.cancel_fall_pulse = False
                self.close_wet_season_gates = True
                self.ramp_rate = None
                self.spring_recession = False
                self.low_wet_season_baseflow = False
                self.high_wet_season_baseflow = False
                self.spring_ramp_up_days = 0.0

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

    def calc_spring_ramp_up_days(self, Qf, Q0, r):
        # t = log(Qsp/Q0)/log(1+r)
        # Qf = (1+r)^t * Q0
        t = math.ceil(log(Qf / Q0, 1 + r))
        return t

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
        fnf_cfs = fnf[timestep.datetime] / 0.0864 * 35.315  # fnf mcm -> cfs

        # Dry season baseflow
        if self.dowy < int(metrics['Wet_Tim']):

            # Pass any flow greater than the 2-year flood (but no more than the 10-year flood)
            if fnf_cfs >= metrics['Peak_2']:
                ifr_cfs = min(fnf_cfs, metrics['Peak_10'])
                self.low_wet_season_baseflow = True

            elif self.low_wet_season_baseflow:
                ifr_cfs = metrics['Wet_BFL_Mag_10']
            else:
                # if metrics['FA_Tim'] <= self.dowy <= metrics['FA_Tim'] + metrics['FA_Dur'] - 1:
                #     ifr_cfs = metrics['FA_Mag']
                yesterday = timestep.datetime - timedelta(days=1)
                tomorrow = timestep.datetime + timedelta(days=1)
                fnf_forecast_mcm = fnf[yesterday:tomorrow].max()
                fa_mag_mcm = metrics['FA_Mag'] / 35.315 * 0.0864
                if fnf_forecast_mcm >= fa_mag_mcm and not self.cancel_fall_pulse:
                    ifr_cfs = fnf_cfs
                    self.fall_pulse_released = True

                else:
                    # use DS_Mag_50 from previous water year
                    ifr_cfs = self.metrics[self.prev_water_year_type]['DS_Mag_50']
                    if self.fall_pulse_released:
                        self.cancel_fall_pulse = True

        # Low wet season baseflow
        elif self.dowy < metrics['SP_Tim']:

            if self.dowy == int(metrics['Wet_Tim']):
                # Calculate spring ramp up start
                self.spring_ramp_up_days \
                    = self.calc_spring_ramp_up_days(metrics['SP_Mag'], metrics['Wet_BFL_Mag_10'], self.ramp_up_rate)

            # Pass any flow greater than the 2-year flood (but no more than the 10-year flood)
            high_flow = False
            if fnf_cfs >= metrics['Peak_2']:
                ifr_cfs = min(fnf_cfs, metrics['Peak_10'])
                self.high_wet_season_baseflow = True
                high_flow = True

            elif self.high_wet_season_baseflow:
                ifr_cfs = metrics['Wet_BFL_Mag_50']
            else:
                ifr_cfs = metrics['Wet_BFL_Mag_10']

            if self.high_wet_season_baseflow:
                self.spring_ramp_up_days = \
                    self.calc_spring_ramp_up_days(metrics['SP_Mag'], metrics['Wet_BFL_Mag_50'], self.ramp_up_rate)

            # Check and see if we should start the spring recession
            if (4, 1) >= (timestep.month, timestep.day) >= (5, 10) \
                    and ifr_cfs >= metrics['SP_Mag'] \
                    and not self.spring_recession:
                self.spring_recession = True

            elif not high_flow:
                # Calculate pre-spring ramp up
                # Qt = Q0 * (1 + r) ^ t
                time_to_spring_peak = self.dowy - (metrics['SP_Tim'] - self.spring_ramp_up_days) + 1
                if time_to_spring_peak >= 0:
                    ifr_cfs = ifr_cfs * (1 + self.ramp_up_rate) ** time_to_spring_peak

        elif self.dowy == metrics['SP_Tim'] and not self.spring_recession:
            ifr_cfs = metrics['SP_Mag']
            self.spring_recession = True

        if 4 <= timestep.month <= 9:

            # ...ramp down rate
            ramp_down_rate = 0.07

            prev_flow_mcm = self.model.nodes[self.res_name].prev_flow[sid]
            ifr_ramp_down_cfs = prev_flow_mcm * (1 - ramp_down_rate) / 0.0864 * 35.315

            if self.spring_recession:
                # Spring recession ramp down
                ifr_cfs = max(ifr_ramp_down_cfs, metrics['DS_Mag_50'])

            else:
                # Non-spring recession ramp down
                ifr_cfs = max(ifr_ramp_down_cfs, ifr_cfs)

            # This releases the minimum of functional flows and full natural flow (with min of Wet_BFL_Mag_10)
            ifr_cfs = min(ifr_cfs, max(fnf_cfs, metrics['Wet_BFL_Mag_10']))

        else:
            # This releases the minimum of functional flows and full natural flow
            ifr_cfs = min(ifr_cfs, fnf_cfs)

        ifr_mcm = ifr_cfs / 35.315 * 0.0864

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
