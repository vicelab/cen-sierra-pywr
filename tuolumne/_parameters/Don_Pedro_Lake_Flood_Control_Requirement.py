from parameters import WaterLPParameter

from utilities.converter import convert


class Don_Pedro_Lake_Flood_Control_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        if self.model.mode == 'planning':
            return 0

        month = self.datetime.month
        day = self.datetime.day
        start_tuple = (month, day)

        # Get target storage
        month_day = '{}-{}'.format(month, day)
        flood_curve = self.model.tables["Don Pedro Lake Flood Control Curve"]
        flood_control_curve_mcm = flood_curve.at[month_day]

        # Get previous storage
        prev_storage_mcm = self.model.nodes["Don Pedro Reservoir"].volume[scenario_index.global_id]

        release_mcm = 0.0
        if prev_storage_mcm >= flood_control_curve_mcm:
            release_mcm += prev_storage_mcm - flood_control_curve_mcm

        release_mcm = min(release_mcm, 8000 * 1.2335)

        return release_mcm / 0.0864

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


Don_Pedro_Lake_Flood_Control_Requirement.register()
print(" [*] Don_Pedro_Lake_Flood_Control_Requirement successfully registered")
