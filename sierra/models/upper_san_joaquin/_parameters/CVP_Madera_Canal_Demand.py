from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class CVP_Madera_Canal_Demand(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):

        today = (self.datetime.month, self.datetime.day)

        # if today <= (4, 1) or (11, 1) <= today:
        #     return 0

        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix, timestep, scenario_index)
        demand_cfs = self.model.tables["CVP Madera Canal demand"][WYT]

        if self.model.mode == 'scheduling':
            demand_cfs = demand_cfs[today]
        else:
            end = (self.datetime.month, self.days_in_month)
            demand_cfs = demand_cfs[today:end].sum()

        demand_cms = demand_cfs / 35.315

        param_name = "Millerton Lake Flood Release/Requirement" + self.month_suffix
        flood_control_reqt_cms = self.model.parameters[param_name].value(timestep, scenario_index) / 0.0864

        demand_cms += flood_control_reqt_cms

        return demand_cms

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


CVP_Madera_Canal_Demand.register()
