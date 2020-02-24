import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class New_Melones_Flood_Control_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # get target storage
        flood_control_req = self.model.tables["New Melones Lake Flood Control"]
        start = '{:02}-{:02}'.format(self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            target_storage = flood_control_req[start]
        else:
            end = '{:02}-{:02}'.format(self.datetime.month, self.days_in_month())
            target_storage = flood_control_req[start:end].mean()

        # TODO: update this if/when flood control can be implemented via code like this
        return 0


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


New_Melones_Flood_Control_Requirement.register()
print(" [*] New_Melones_Flood_Control_Requirement successfully registered")
