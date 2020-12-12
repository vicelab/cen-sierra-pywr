from sierra.base_parameters import IFRParameter
from sierra.utilities.converter import convert


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
