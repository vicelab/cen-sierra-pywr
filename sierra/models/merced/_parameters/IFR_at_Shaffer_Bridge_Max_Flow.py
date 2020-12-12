from sierra.base_parameters import FlowRangeParameter
from sierra.utilities.converter import convert


class IFR_at_Shaffer_Bridge_Max_Flow(FlowRangeParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    def _value(self, timestep, scenario_index):

        ifr_val = 250 / 35.31  # cfs to cms (16.5 cfs)
        ifr_range_cms = self.get_ifr_range(timestep, scenario_index, initial_value=ifr_val, rate=10)

        return ifr_range_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_at_Shaffer_Bridge_Max_Flow.register()
