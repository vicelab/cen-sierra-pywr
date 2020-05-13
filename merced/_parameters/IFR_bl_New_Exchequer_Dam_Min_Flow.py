from parameters import MinFlowParameter


class IFR_bl_New_Exchequer_Dam_Min_Flow(MinFlowParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    def _value(self, timestep, scenario_index):
        ifr_mcm = 0.061164

        return ifr_mcm

    def value(self, *args, **kwargs):
        ifr = self.get_ifr(*args, **kwargs)
        if ifr is not None:
            return ifr
        else:
            return self._value(*args, **kwargs)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_New_Exchequer_Dam_Min_Flow.register()
