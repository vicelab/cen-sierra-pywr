from sierra.base_parameters import MinFlowParameter
from sierra.utilities.converter import convert


class IFR_bl_New_Exchequer_Dam_Min_Flow(MinFlowParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    def _value(self, timestep, scenario_index):
        ifr_cms = 0.061164 / 0.0864

        return ifr_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_New_Exchequer_Dam_Min_Flow.register()
