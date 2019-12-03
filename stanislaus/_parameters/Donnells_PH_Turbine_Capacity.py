import datetime
import calendar
from parameters import WaterLPParameter

from utilities.converter import convert


class Donnells_PH_Turbine_Capacity(WaterLPParameter):

    def _value(self, timestep, scenario_index):
        capacity_cms = 700 / 35.31  # cfs to cms
        if self.model.mode == 'scheduling':
            if (6, 1) <= (timestep.month, timestep.day) <= (8, 1):
                capacity_cms = 100 / 35.31
            donnells_reservoir = self.model.nodes['Donnells Reservoir']
            # relief_reservoir = self.model.nodes['Relief Reservoir']
            if timestep.index == 0:
                prev_donnell_storage = donnells_reservoir.initial_volume
                # prev_relief_storage = relief_reservoir.initial_volume
            else:
                prev_donnell_storage = donnells_reservoir.volume[-1]
                # prev_relief_storage = relief_reservoir.volume[-1]
            prev_donnell_storage /= 1.2335
            # prev_relief_storage /= 1.2335

            # if prev_donnell_storage <= 20 or prev_relief_storage <= 2.5:
            if prev_donnell_storage <= 20:
                capacity_cms = 100 / 35.31  # curtail to 12.5 cfs
            # elif prev_donnell_storage <= 40 or prev_relief_storage <= 5.5:
            elif prev_donnell_storage <= 40:
                capacity_cms = 350 / 35.31  # curtail to 12.5 cfs

        else:
            if self.datetime.month in [6, 7, 8]:
                capacity_cms = 100 / 35.31
            capacity_cms *= self.days_in_month()

        return capacity_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Donnells_PH_Turbine_Capacity.register()
print(" [*] Donnells_PH_Turbine_Capacity successfully registered")
