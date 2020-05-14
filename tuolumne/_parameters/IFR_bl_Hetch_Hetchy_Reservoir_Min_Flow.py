from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        base_flow_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Base Flow"].get_value(scenario_index)
        UTREP_spill_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/UTREP Spill"].get_value(scenario_index)
        IFR_mcm = max(base_flow_mcm, UTREP_spill_mcm)

        IFR_cms = IFR_mcm / 0.0864 # convert to cms

        return IFR_cms

    def value(self, *args, **kwargs):
        try:
            ifr = self.get_ifr(*args, **kwargs)
            if ifr is not None:
                return ifr
            else:
                ifr = self._value(*args, **kwargs)
                return ifr # unit is already mcm
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow.register()
