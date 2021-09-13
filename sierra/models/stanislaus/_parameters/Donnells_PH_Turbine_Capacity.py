from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Donnells_PH_Turbine_Capacity(BaseParameter):

    def _value(self, timestep, scenario_index):
        capacity_cms = 700 / 35.31  # cfs to cms
        if self.model.mode == 'scheduling':
            # pass
            # if (7, 1) <= (timestep.month, timestep.day) <= (8, 1):
            #     capacity_cms *= 2/3

            donnells_reservoir = self.model.nodes['Donnells Reservoir']
            max_volume = donnells_reservoir.max_volume
            # relief_reservoir = self.model.nodes['Relief Reservoir']
            if timestep.index == 0:
                prev_donnell_storage = donnells_reservoir.initial_volume
                # prev_relief_storage = relief_reservoir.initial_volume
            else:
                prev_donnell_storage = donnells_reservoir.volume[scenario_index.global_id]
                # prev_relief_storage = relief_reservoir.volume[scenario_index.global_id]
            prev_donnell_storage /= 1.2335

            storage_fraction = prev_donnell_storage / max_volume
            if storage_fraction <= 0.5:
                capacity_cms *= storage_fraction

        else:
            # if self.datetime.month in [6, 7, 8]:
            #     capacity_cms = 100 / 35.31
            capacity_cms *= self.days_in_month

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
