from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Spring_Gap_PH_Turbine_Capacity(BaseParameter):

    def _value(self, timestep, scenario_index):
        capacity_cms = 62 / 35.31  # cfs to cms
        if self.model.mode == 'scheduling':
            if (7, 1) <= (timestep.month, timestep.day) <= (8, 31):
                capacity_cms = 12.5 / 35.31
            elif timestep.month >= 9:
                pinecrest_reservoir = self.model.nodes['Pinecrest Reservoir']
                if timestep.index == 0:
                    prev_storage = pinecrest_reservoir.initial_volume
                else:
                    prev_storage = pinecrest_reservoir.volume[scenario_index.global_id]
                prev_storage_taf = prev_storage / 1.2335

                if prev_storage_taf <= 5:  # taf to mcm
                    capacity_cms *= 0.25  # curtail to 12.5 cfs
                elif prev_storage_taf <= 10:
                    capacity_cms *= 0.75  # curtail to 25 cfs

        else:
            if self.datetime.month in [7, 8]:
                capacity_cms = 12.5 / 35.31
            # elif self.datetime.month == 8:
            #     capacity_cms = (12.5 + 57) / 2 / 35.31  # average of 12.5 and 57
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


Spring_Gap_PH_Turbine_Capacity.register()
