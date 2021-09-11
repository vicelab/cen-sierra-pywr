from sierra.base_parameters import BaseParameter


class USBR_Big_Creek_WYT(BaseParameter):
    """"""

    wyt = 1  # assume a normal year

    def _value(self, timestep, scenario_index):

        Friant_Apr_Jul_runoff_af = self.model.tables['Seasonal Inflow at Friant'][self.operational_water_year]
        if Friant_Apr_Jul_runoff_af <= 900000:
            wyt = 1  # dry
        else:
            wyt = 2  # normal

        return wyt

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


USBR_Big_Creek_WYT.register()

