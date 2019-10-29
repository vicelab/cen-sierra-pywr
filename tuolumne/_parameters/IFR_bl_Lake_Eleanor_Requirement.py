from parameters import WaterLPParameter

from utilities.converter import convert

import pandas


class IFR_bl_Lake_Eleanor_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)

        if timestep.index == 0:
            schedule = self.model.parameters["IFR bl Lake Eleanor/IFR Schedule"].array()
            self.ifr_lookup = pandas.DataFrame(data=schedule[1:, 1:], index=schedule[1:, 0])

        is_pumping = 1

        month_name = timestep.datetime.strftime("%B")  # e.g., "January"
        if timestep.month in [4, 9]:
            if timestep.day <= 10:
                part = 10
            elif timestep.day <= 20:
                part = 20
            else:
                part = 30
            ifr_period = '{}_{}'.format(month_name, part)
        else:
            ifr_period = month_name

        ifr = self.ifr_lookup[is_pumping][ifr_period]

        return ifr

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


IFR_bl_Lake_Eleanor_Requirement.register()
print(" [*] IFR_bl_Lake_Eleanor_Requirement successfully registered")
