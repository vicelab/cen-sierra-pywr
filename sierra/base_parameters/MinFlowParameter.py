import math
import random
from dateutil.relativedelta import relativedelta
from math import log
from datetime import datetime, timedelta
from sierra.base_parameters import IFRParameter

DRY = 'dry'
WET = 'wet'
RECESSION = 'recession'


class FlowPeriods(object):
    DRY_SEASON = 'dry season'
    FALL_PULSE = 'fall pulse'
    WET_SEASON = 'wet season'
    SPRING_RECESSION = 'spring recession'


class MinFlowParameter(IFRParameter):
    water_year_type = None
    params = None
    include_functional_flows = False

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        for s in self.model.scenarios.scenarios:
            if 'Functional Flows' in s.ensemble_names:

                self.include_functional_flows = True
                self.metrics = self.model.tables['functional flows metrics']
                self.water_year_type = 'moderate'
                self.ramp_up_rate = 0.13
                self.ramp_down_rate = 0.07

                self.water_year_types = {
                    1: 'dry',
                    2: 'moderate',
                    3: 'wet'
                }

                self.prev_requirement = [0] * self.num_scenarios

    def before(self):
        super().before()

        timestep = self.model.timestep

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
                self.season = DRY

                metrics = self.metrics[self.water_year_type]
                self.wet_season_baseflow = metrics['Wet_BFL_Mag_10']
                self.spring_ramp_up_start \
                    = self.calc_spring_ramp_up_start(metrics['Wet_BFL_Mag_10'], metrics['SP_Mag'], metrics['SP_Tim'])

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

        elif scenario_name == 'Functional Flows' and self.ifr_type == 'enhanced':
            if self.model.mode == 'scheduling':
                min_flow_mcm = self.functional_flows_min_flow_scheduling(timestep, scenario_index, scenario_name)
            else:
                min_flow_mcm = self.functional_flows_min_flow_planning(timestep, scenario_index, scenario_name)
                
        elif scenario_name == 'SWRCB' and self.ifr_type == 'enhanced':
            baseflow_mcm = default(timestep, scenario_index)

            min_flow_mcm = self.swrcb_flows_min_flow(timestep, scenario_index, baseflow_mcm)              

        elif default:
            min_flow_mcm = default(timestep, scenario_index)

        return min_flow_mcm

    def swrcb_flows_min_flow(self, timestep, scenario_index, baseflow_mcm):
        ifr_mcm = baseflow_mcm*0.0864
        if 2 <= timestep.month <= 6:
            start_date = timestep.datetime - relativedelta(days=7)
            ifr_swrcb = self.model.parameters['Full Natural Flow'].dataframe[start_date:timestep.datetime].mean()*0.4
            ifr_mcm = max(ifr_swrcb, ifr_mcm)
        ifr_cms = ifr_mcm/0.0864
        return ifr_cms

    def calc_spring_ramp_up_days(self, Q0, Qf, r):
        # t = log(Qsp/Q0)/log(1+r)
        # Qf = (1+r)^t * Q0
        t = math.ceil(log(Qf / Q0, 1 + r))
        return t

    def calc_spring_ramp_up_start(self, Q0, Qf, Tf):
        spring_ramp_up_days_total \
            = self.calc_spring_ramp_up_days(Q0, Qf, self.ramp_up_rate)
        spring_ramp_up_start = Tf - spring_ramp_up_days_total
        return spring_ramp_up_start

    def calc_ramp_down_cfs(self, ifr_cfs, sid):
        prev_flow_mcm = self.model.nodes[self.res_name].prev_flow[sid]
        ifr_ramp_down_cfs = prev_flow_mcm * (1 - self.ramp_down_rate) / 0.0864 * 35.315
        ifr_cfs = max(ifr_ramp_down_cfs, ifr_cfs)
        return ifr_cfs

    def functional_flows_min_flow_scheduling(self, timestep, scenario_index, scenario_name=None):
        """
        Calculate the minimum functional flow
        :param timestep:
        :param scenario_index:
        :return:
        """
        sid = scenario_index.global_id

        metrics = self.metrics[self.water_year_type]

        ifr_cfs = 0.0
        fnf = self.model.parameters['Full Natural Flow'].dataframe
        fnf_cfs = fnf[timestep.datetime] / 0.0864 * 35.315  # fnf mcm -> cfs

        # Dry season baseflow
        if self.dowy < int(metrics['Wet_Tim']) and not self.season == WET:

            # Pass any flow greater than the 2-year flood (but no more than the 10-year flood)
            if fnf_cfs >= metrics['Peak_2']:
                ifr_cfs = min(fnf_cfs, metrics['Peak_10'])
                self.season = WET
            else:
                # if metrics['FA_Tim'] <= self.dowy <= metrics['FA_Tim'] + metrics['FA_Dur'] - 1:
                #     ifr_cfs = metrics['FA_Mag']
                yesterday = timestep.datetime - timedelta(days=1)
                tomorrow = timestep.datetime + timedelta(days=1)
                fnf_forecast_mcm = fnf[yesterday:tomorrow].max()
                fa_mag_mcm = metrics['FA_Mag'] / 35.315 * 0.0864

                if fnf_forecast_mcm >= fa_mag_mcm and not self.cancel_fall_pulse:
                    ifr_cfs = fnf_cfs
                    if fnf_forecast_mcm == fnf[yesterday]:
                        self.cancel_fall_pulse = True

                else:
                    # use DS_Mag_50 from previous water year
                    ifr_cfs = self.metrics[self.prev_water_year_type]['DS_Mag_50']
                    # if self.fall_pulse_released:
                    #     self.cancel_fall_pulse = True

        # Low wet season baseflow
        elif self.dowy < metrics['SP_Tim'] and self.season != RECESSION:
            self.season = WET
            if self.dowy >= self.spring_ramp_up_start:
                # Calculate pre-spring ramp up: Qt = Q0 * (1 + r) ^ t
                spring_ramp_up_days = self.dowy - self.spring_ramp_up_start
                ifr_cfs = min(self.wet_season_baseflow * (1 + self.ramp_up_rate) ** spring_ramp_up_days,
                              metrics['SP_Mag'])
                if ifr_cfs >= metrics['SP_Mag']:
                    self.season = RECESSION

            # Pass any flow greater than the 2-year flood (but no more than the 10-year flood)
            # high_flow = False
            elif fnf_cfs >= metrics['Peak_2']:
                ifr_cfs = min(fnf_cfs, metrics['Peak_10'])
                if self.dowy >= metrics['Wet_Tim']:
                    self.wet_season_baseflow = metrics['Wet_BFL_Mag_50']
                # high_flow = True
                self.spring_ramp_up_start \
                    = self.calc_spring_ramp_up_start(self.wet_season_baseflow, metrics['SP_Mag'], metrics['SP_Tim'])

            elif fnf_cfs >= metrics['SP_Mag']:
                ifr_cfs = fnf_cfs

            else:
                ifr_cfs = self.wet_season_baseflow
                if self.wet_season_baseflow == metrics['Wet_BFL_Mag_10']:
                    ifr_min = fnf_cfs
                else:
                    ifr_min = max(fnf_cfs, metrics['Wet_BFL_Mag_10'])
                ifr_cfs = min(ifr_cfs, ifr_min)

            if 4 <= timestep.month <= 9:
                ifr_cfs = self.calc_ramp_down_cfs(ifr_cfs, sid)

                # Check and see if we should start the spring recession
                if ifr_cfs >= metrics['SP_Mag'] and self.dowy < self.spring_ramp_up_start:
                    ifr_cfs = max(ifr_cfs, self.wet_season_baseflow)
                    self.spring_ramp_up_start = self.dowy
                    # self.season = RECESSION

        elif self.season != DRY:
            if self.dowy == metrics['SP_Tim'] and not self.season == RECESSION:
                ifr_cfs = metrics['SP_Mag']

            else:
                ifr_cfs = self.calc_ramp_down_cfs(ifr_cfs, sid)
                ifr_cfs = max(ifr_cfs, metrics['DS_Mag_50'])
                if ifr_cfs == metrics['DS_Mag_50']:
                    self.season = DRY
        else:
            ifr_cfs = min(metrics['DS_Mag_50'], fnf_cfs)

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
