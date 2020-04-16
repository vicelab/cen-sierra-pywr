from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        base_flow_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Base Flow"].value(timestep, scenario_index)
        UTREP_spill_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/UTREP Spill"].get_value(scenario_index)
        IFR_mcm = max(base_flow_mcm, UTREP_spill_mcm)

        IFR_cms = IFR_mcm / 0.0864 # convert to cms

        return IFR_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow.register()
