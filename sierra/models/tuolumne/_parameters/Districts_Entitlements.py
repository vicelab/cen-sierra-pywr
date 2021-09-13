from sierra.base_parameters import BaseParameter


class Districts_Entitlements(BaseParameter):

    def _value(self, timestep, scenario_index):

        # Districts Entitlements is the lesser of full natural flow at La Grange and a maximum value:
        # Jun 15-Apr 14: 4792.1 AF/day = 5.911 mcm
        # Apr 15-Jun 14 : 8064.8 AF/day = 9.948 mcm

        fnf_mcm = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)

        if (4, 15) <= (timestep.month, timestep.day) <= (6, 14):
            max_entitlement_mcm = 9.948
        else:
            max_entitlement_mcm = 5.911

        return min(fnf_mcm, max_entitlement_mcm)

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
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


Districts_Entitlements.register()
