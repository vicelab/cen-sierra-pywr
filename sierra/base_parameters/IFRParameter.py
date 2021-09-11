from sierra.base_parameters import BaseParameter


class IFRParameter(BaseParameter):
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
