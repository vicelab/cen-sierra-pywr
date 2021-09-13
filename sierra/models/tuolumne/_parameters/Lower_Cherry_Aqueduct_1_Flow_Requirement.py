from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Lower_Cherry_Aqueduct_1_Flow_Requirement(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):

        hh = self.model.nodes["Hetch Hetchy Reservoir"].volume[scenario_index.global_id]
        demand_reduction = self.model.parameters["SFPUC requirement/Demand Reduction"].get_value(scenario_index)
        if demand_reduction == 0.25 and hh <= 135:
            flow_cms = 6.5
        else:
            flow_cms = 0.0

        return flow_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000)
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


Lower_Cherry_Aqueduct_1_Flow_Requirement.register()
