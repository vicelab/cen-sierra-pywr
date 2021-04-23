from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        base_flow_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Base Flow"].get_value(scenario_index)
        UTREP_spill_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/UTREP Spill"].get_value(scenario_index)
        IFR_mcm = max(base_flow_mcm, UTREP_spill_mcm)

        IFR_cms = IFR_mcm / 0.0864 # convert to cms

        return IFR_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow.register()
