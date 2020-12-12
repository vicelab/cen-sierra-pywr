from dateutil.relativedelta import relativedelta
import random
from calendar import monthrange

import pandas as pd
from pywr.parameters import Parameter

from sierra.utilities.converter import convert


class Timestep(object):
    step = None
    datetime = None
    year = None
    month = None


class WaterLPParameter(Parameter):
    cfs_to_cms = 1 / 35.315

    mode = 'scheduling'
    res_class = 'network'
    res_name = None
    res_name_full = None
    attr_name = None
    block = None
    month = None
    year = None
    days_in_month = None
    month_offset = None
    month_suffix = ''
    demand_constant_param = ''
    elevation_param = ''
    num_scenarios = 0

    timestep = Timestep()

    def setup(self):
        super().setup()

        self.num_scenarios = len(self.model.scenarios.combinations)

        self.mode = getattr(self.model, 'mode', self.mode)

        name_parts = self.name.split('/')
        self.res_name = name_parts[0]

        if len(name_parts) >= 2:
            self.attr_name = name_parts[1]

        if self.mode == 'scheduling':
            if len(name_parts) == 3:
                self.block = int(name_parts[2])
        else:
            if len(name_parts) >= 2:
                self.month_offset = int(name_parts[-1]) - 1
            if len(name_parts) == 4:
                self.block = int(name_parts[-2])

        if self.month_offset is not None:
            self.month_suffix = '/{}'.format(self.month_offset + 1)

        try:
            node = self.model.nodes[self.res_name + self.month_suffix]
        except:
            node = None

        if node and 'level' in node.component_attrs or self.attr_name == 'Storage Value':
            self.elevation_param = '{}/Elevation'.format(self.res_name) + self.month_suffix

    def before(self):
        super(WaterLPParameter, self).before()
        self.datetime = self.model.timestepper.current.datetime

        if self.model.mode == 'planning':
            if self.month_offset:
                self.datetime += relativedelta(months=+self.month_offset)

            self.year = self.datetime.year
            self.month = self.datetime.month

        if 4 <= self.datetime.month <= 12:
            self.operational_water_year = self.datetime.year
        else:
            self.operational_water_year = self.datetime.year - 1

        if self.datetime.day == 1:
            self.days_in_month = monthrange(self.datetime.year, self.datetime.month)[1]

    def get(self, param, timestep, scenario_index):
        return self.model.parameters[param].value(timestep, scenario_index)

    def get_days_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return monthrange(year, month)[1]

    def get_dates_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        start = pd.datetime(year, month, 1)
        ndays = monthrange(year, month)[1]
        dates = pd.date_range(start, periods=ndays).tolist()
        return dates


class IFRParameter(WaterLPParameter):
    ifrs_idx = None
    ifr_names = None
    ifr_type = 'basic'

    def setup(self):
        super().setup()

        self.ifr_type = self.model.nodes[self.res_name + self.month_suffix].ifr_type

        scenario_names = [s.name for s in self.model.scenarios.scenarios]
        self.ifrs_idx = scenario_names.index('IFRs') if 'IFRs' in scenario_names else None
        if self.ifrs_idx is not None:
            self.ifr_names = self.model.scenarios.scenarios[self.ifrs_idx].ensemble_names


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
                self.params = self.model.tables['functional flows parameters']
                self.metrics = self.model.tables['functional flows metrics']
                self.water_year_type = 'moderate'
                self.magnitude_col = 'moderate magnitude'

                self.water_year_types = {
                    1: 'dry',
                    2: 'moderate',
                    3: 'wet'
                }

                # self.dry_season_baseflow_mcm = self.params.at['dry season baseflow', self.magnitude_col] \
                #                                / 35.31 * 0.0864
                self.prev_requirement = [0] * self.num_scenarios
                self.flood_days = [0] * self.num_scenarios
                self.flood_duration = [0] * self.num_scenarios
                self.prev_flood_mcm = [0] * self.num_scenarios
                self.flood_year = [0] * self.num_scenarios

                # 2-year flood: 18670 cfs x 7 days = 320 mcm flood total
                # 5-year flood: 40760 cfs x 2 days = 199 mcm flood total
                # 10-year flood: 52940 cfs x 2 days = 259 mcm flood total
                floods = self.model.tables['functional flows floods']
                self.flood_lengths = flood_lengths = {10: 2, 5: 2, 2: 7}  # these should be from highest to lowest
                self.flood_volumes_mcm = {}
                for return_interval in flood_lengths:
                    self.flood_volumes_mcm[return_interval] \
                        = floods['{}-year'.format(return_interval)] / 35.315 * 0.0864 * flood_lengths[return_interval]

    def before(self):
        super().before()

        timestep = self.model.timestep

        if timestep.month >= 10:
            dowy = timestep.dayofyear - 275 + 1
        else:
            dowy = timestep.dayofyear + 92 - 1
        self.dowy = dowy

        if self.include_functional_flows:
            self.wet_baseflow_start = 100
            self.spring_recession_start = 250

            if timestep.month == 10 and timestep.day == 1:
                # update water year type, assuming perfect foresight
                wy = timestep.year + 1
                fnf = self.model.tables['Annual Full Natural Flow']
                fnf_wy = fnf[wy]
                terciles = fnf.quantile([0, 0.33, 0.66]).values
                wyt = sum([1 for q in terciles if fnf_wy >= q])
                self.water_year_type = self.water_year_types[wyt]

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
                min_flow_mcm = self.functional_flows_min_flow_scheduling(timestep, scenario_index)
            else:
                min_flow_mcm = self.functional_flows_min_flow_planning(timestep, scenario_index)

        elif default:
            min_flow_mcm = default(timestep, scenario_index)

        return min_flow_mcm

    def swrcb_flows_min_flow(self, timestep, scenario_index):
        fnf_mcm = self.model.parameters['Full Natural Flow'].get_value(scenario_index)
        ifr_mcm = fnf_mcm * 0.4
        ifr_cms = ifr_mcm / 0.0864
        return ifr_cms

    def functional_flows_min_flow_scheduling(self, timestep, scenario_index):
        """
        Calculate the minimum functional flow
        :param timestep:
        :param scenario_index:
        :return:
        """
        sid = scenario_index.global_id

        params = self.params[self.water_year_type]
        metrics = self.metrics[self.water_year_type]
        dowys = params['DOWY']
        flows = params['mag_cfs']

        ifr_mcm = 0.0
        ifr_cfs = 0.0
        fnf = self.model.parameters['Full Natural Flow']

        # Dry season baseflow
        if self.dowy <= dowys['fall base 2 end']:

            if dowys['fall pulse start'] <= self.dowy <= dowys['fall pulse end']:
                ifr_cfs = flows['fall pulse start']

            else:
                ifr_cfs = flows['fall base 1 start']

        # Low wet season baseflow
        elif self.dowy <= dowys['median wet baseflow']:
            # TODO: change logic as follows
            # 1. Start by releasing all inflow
            # 2. If a 2-year flood has passed (i.e., look back 7 days), then drop to the 10th percentile base flow
            # 3. Look forward 2-7 days and release incoming 2, 5, or 10 year event

            mbf_start = dowys['low wet baseflow']
            mbf_end = dowys['median wet baseflow']
            mbf_start_cfs = flows['low wet baseflow']
            mbf_end_cfs = flows['median wet baseflow']
            daily_increment = (mbf_end_cfs - mbf_start_cfs) / (mbf_end - mbf_start)
            days_since_start = self.dowy - mbf_start
            ifr_cfs = mbf_start_cfs + daily_increment * days_since_start

        # Median wet season baseflow
        elif self.dowy <= dowys['final wet baseflow']:
            ifr_cfs = flows['median wet baseflow']

        # Spring recession
        elif self.dowy == dowys['spring recession start']:
            ifr_cfs = flows['spring recession start']

        # ...ramp down
        else:
            ramp_rate = 0.07
            prev_flow_mcm = self.model.nodes[self.res_name].prev_flow[sid]
            ifr_cfs = prev_flow_mcm * (1 - ramp_rate) / 0.0864 * 35.315
            ifr_cfs = max(ifr_cfs, flows['fall base 1 start'])

        # winter flood season rules
        winter_flood_mcm = 0
        winter_flood_cfs = 0
        winter_flood_season = dowys['low wet baseflow'] <= self.dowy <= dowys['final wet baseflow']

        if winter_flood_season or self.prev_flood_mcm[sid]:

            if self.flood_days[sid] < self.flood_duration[sid]:
                winter_flood_mcm = self.prev_flood_mcm[sid]  # TODO: make scenario-safe

            elif self.water_year_type == 'moderate':
                flood_start = metrics['Peak_Tim_2']
                if self.dowy == flood_start:
                    self.flood_duration[sid] = metrics['Peak_Dur_2']
                    winter_flood_cfs = metrics['Peak_2']

            elif self.water_year_type == 'wet':
                flood_starts = {}
                for interval in [2, 5, 10]:
                    peak_timing = metrics['Peak_Tim_{}'.format(interval)]
                    flood_starts[peak_timing] = interval
                    if interval == 2:
                        # add in additional 2-year floods
                        for i in range(metrics['Peak_Fre_2']):
                            flood_starts[peak_timing + 30 * (i - 1)] = interval
                if self.dowy in flood_starts:
                    return_interval = flood_starts[self.dowy]
                    self.flood_duration[sid] = metrics['Peak_Dur_{}'.format(return_interval)]
                    winter_flood_cfs = metrics['Peak_{}'.format(return_interval)]

            if winter_flood_cfs:
                winter_flood_mcm = winter_flood_cfs / 35.315 * 0.0864

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
            #         forecast_mcm = fnf.dataframe[forecast_start:forecast_start + relativedelta(days=days)].sum()
            #         if forecast_mcm >= flood_volume_mcm:
            #             winter_flood_mcm = flood_volume_mcm / days
            #             self.flood_year[sid] = return_interval
            #             break

            if winter_flood_mcm:
                self.prev_flood_mcm[sid] = winter_flood_mcm
                self.flood_days[sid] += 1
                # self.num_floods[sid] = min(self.num_floods[sid] + 1, 2)
            else:
                self.prev_flood_mcm[sid] = 0
                self.flood_days[sid] = 0
                self.flood_duration[sid] = 0
                self.flood_year[sid] = 0

        ifr_mcm = ifr_mcm or (ifr_cfs / 35.315 * 0.0864)
        ifr_mcm = max(ifr_mcm, winter_flood_mcm)

        fnf_mcm = fnf.dataframe[timestep.datetime]
        ifr_mcm = min(ifr_mcm, fnf_mcm)

        self.prev_requirement[sid] = ifr_mcm

        ifr_cms = ifr_mcm / 0.0864

        return ifr_cms

    def functional_flows_min_flow_planning(self, timestep, scenario_index):
        """
        Calculate the minimum functional flow
        :param timestep:
        :param scenario_index:
        :return:
        """
        sid = scenario_index.global_id

        params = self.params

        ifr_mcm = 0.0
        ifr_cfs = 0.0
        fnf = self.model.parameters['Full Natural Flow']

        # Dry season baseflow
        if self.dowy < params.at['fall pulse', 'earliest']:
            ifr_cfs = params.at['dry season baseflow', self.magnitude_col]

        # Fall pulse
        elif self.dowy == params.at['fall pulse', 'earliest']:
            pulse_flow_idx = list(params.columns).index('dry magnitude') + random.randint(1, 3) - 1
            # pulse_flow_idx = list(params.columns).index('dry magnitude') + 3 - 1
            pulse_flow_col = params.columns[pulse_flow_idx]
            ifr_cfs = params.at['fall pulse', pulse_flow_col]

        elif self.dowy < params.at['fall pulse', 'latest']:
            ifr_mcm = self.prev_requirement[sid]

        elif self.dowy == params.at['fall pulse', 'latest']:
            ifr_mcm = self.model.nodes[self.res_name].prev_flow[sid] * 0.2

        # Low wet season baseflow
        elif self.dowy < self.wet_baseflow_start:
            ifr_mcm = fnf.get_value(scenario_index) * 0.5

        # Median wet season baseflow
        elif self.dowy < self.spring_recession_start:
            ifr_cfs = params.at['median wet baseflow', self.magnitude_col]

        # Spring recession
        elif self.dowy == self.spring_recession_start:
            ifr_cfs = params.at['spring recession start', self.magnitude_col]

        # ...ramp down
        else:
            ramp_rate = params.at['spring recession rate', self.magnitude_col]
            prev_flow = self.model.nodes[self.res_name].prev_flow[sid]
            ifr_mcm = prev_flow * (1 - ramp_rate)
            ifr_mcm = max(ifr_mcm, self.dry_season_baseflow_mcm)

        # winter flood season rules
        winter_flood_mcm = 0
        winter_flood_season = params.at['fall pulse', 'latest'] < self.dowy < self.spring_recession_start \
                              or self.prev_flood_mcm[sid]
        if winter_flood_season:
            # 2-year flood: 18670 cfs x 7 days = 320 mcm flood total
            # 5-year flood: 40760 cfs x 2 days = 199 mcm flood total
            # 10-year flood: 52940 cfs x 2 days = 259 mcm flood total
            forecast_start = timestep.datetime
            fnf_forecast_7d = fnf.dataframe[forecast_start:forecast_start + relativedelta(days=7)].sum()
            fnf_forecast_2d = fnf.dataframe[forecast_start:forecast_start + relativedelta(days=2)].sum()

            if self.flood_year[sid] and self.flood_days[sid] < self.flood_lengths[self.flood_year[sid]]:
                winter_flood_mcm = self.prev_flood_mcm[sid]  # TODO: make scenario-safe

            # 10-year flood
            elif fnf_forecast_2d >= 259:
                winter_flood_mcm = 259
                self.flood_year[sid] = 10

            # 5-year flood
            elif fnf_forecast_2d >= 199:
                winter_flood_mcm = 199
                self.flood_year[sid] = 5

            # 2-year flood
            elif fnf_forecast_7d >= 320:
                winter_flood_mcm = 320
                self.flood_year[sid] = 2

            if winter_flood_mcm:
                self.prev_flood_mcm[sid] = winter_flood_mcm
                self.flood_days[sid] += 1
                # self.num_floods[sid] = min(self.num_floods[sid] + 1, 2)
            else:
                self.prev_flood_mcm[sid] = 0
                self.flood_days[sid] = 0
                self.flood_year[sid] = 0

        ifr_mcm = ifr_mcm or (ifr_cfs / 35.315 * 0.0864)

        self.prev_requirement[sid] = ifr_mcm

        ifr_cms = ifr_mcm / 0.0864

        return ifr_cms


class FlowRangeParameter(IFRParameter):
    def requirement(self, timestep, scenario_index, default=None):
        """
        Calculate a custom IFR other than the baseline IFR
        :param timestep:
        :param scenario_index:
        :return:
        """

        scenario_name = None
        if self.ifrs_idx is not None:
            scenario_name = self.ifr_names[scenario_index.indices[self.ifrs_idx]]

        flow_range = 1e9

        if scenario_name == 'No IFRs':
            pass

        elif scenario_name == 'Functional Flows' and self.ifr_type == 'enhanced':
            flow_range = self.functional_flows_range(timestep, scenario_index)

        elif default:
            flow_range = default(timestep, scenario_index)

        flow_range_mcm = convert(flow_range, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

        return flow_range_mcm

    def functional_flows_range(self, timestep, scenario_index):
        FNF = self.model.parameters['Full Natural Flow'].value(timestep, scenario_index)
        return FNF * 0.4 / 0.0864

    def get_ifr_range(self, timestep, scenario_index, **kwargs):
        param_name = self.res_name + '/Min Flow' + self.month_suffix
        # min_ifr = self.model.parameters[param_name].get_value(scenario_index) / 0.0864  # convert to cms
        min_ifr = self.model.parameters[param_name].value(timestep, scenario_index) / 0.0864  # convert to cms
        max_ifr = self.get_up_ramp_ifr(timestep, scenario_index, **kwargs)

        ifr_range = max(max_ifr - min_ifr, 0.0)

        return ifr_range

    def get_up_ramp_ifr(self, timestep, scenario_index, initial_value=None, rate=0.25, max_flow=None):

        if self.model.mode == 'scheduling':
            if initial_value is None:
                raise Exception('Initial maximum ramp up rate cannot be None')
            if timestep.index == 0:
                Qp = initial_value  # should be in cms
            else:
                Qp = self.model.nodes[self.res_name].prev_flow[scenario_index.global_id] / 0.0864  # convert to cms
            qmax = Qp * (1 + rate)
        else:
            qmax = 1e6

        if max_flow is not None:
            qmax = min(qmax, max_flow)

        return qmax
