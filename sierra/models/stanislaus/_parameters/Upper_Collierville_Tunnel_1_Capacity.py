from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Upper_Collierville_Tunnel_1_Capacity(BaseParameter):

    def _value(self, timestep, scenario_index):
        capacity_cms = 800 / 35.31  # cfs to cms
        if self.model.mode == 'scheduling':
            if (6, 1) <= (timestep.month, timestep.day) <= (8, 1):
                capacity_cms = 100 / 35.31
            union_utica = self.model.nodes['Union-Utica Reservoir']
            # relief_reservoir = self.model.nodes['Relief Reservoir']
            if timestep.index == 0:
                prev_storage = union_utica.initial_volume
            else:
                prev_storage = union_utica.volume[scenario_index.global_id]
            prev_storage /= 1.2335

            if prev_storage <= 2:
                capacity_cms = 0
            elif prev_storage <= 3:
                capacity_cms = 150 / 35.31
            elif prev_storage <= 4:
                capacity_cms = 300 / 35.31

        else:
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


Upper_Collierville_Tunnel_1_Capacity.register()
