import pandas as pd
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from pywr.parameters import Parameter
from utilities.converter import convert
from utilities.decorators import catch

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


class MinFlowParameter(IFRParameter):

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
            pass

        elif scenario_name == 'Functional Flows' and self.ifr_type == 'enhanced':
            min_flow_mcm = self.functional_flows_min_flow(timestep, scenario_index)

        elif default:
            min_flow_mcm = default(timestep, scenario_index)

        return min_flow_mcm

    def functional_flows_min_flow(self, timestep, scenario_index):
        FNF = self.model.parameters['Full Natural Flow'].value(timestep, scenario_index)
        return FNF * 0.4


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
