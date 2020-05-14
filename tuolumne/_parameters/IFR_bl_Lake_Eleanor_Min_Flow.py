from parameters import MinFlowParameter

from utilities.converter import convert


class IFR_bl_Lake_Eleanor_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # Determine whether or not we are pumping
        # TODO: put this into a parameter?
        is_transferring = self.model.parameters["Eleanor-Cherry Pumping Station/Requirement"] \
                              .value(timestep, scenario_index) > 0.0
        CH_elev = self.model.nodes["Cherry Lake"].get_level(scenario_index)
        EL_elev = self.model.nodes["Lake Eleanor"].get_level(scenario_index)

        is_pumping = is_transferring and CH_elev >= EL_elev

        # Calculate IFR, in cfs
        if is_pumping:
            md = (self.datetime.month, self.datetime.day)
            if (4, 1) <= md <= (5, 14) or (9, 16) <= md <= (10, 31):
                ifr = 10
            elif (5, 15) <= md <= (9, 15):
                ifr = 20
            else:
                ifr = 5

        else:
            if 7 <= self.datetime.month <= 9:
                ifr = 15.5
            else:
                ifr = 5

        return ifr / 35.315  # convert to cms

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


IFR_bl_Lake_Eleanor_Min_Flow.register()
