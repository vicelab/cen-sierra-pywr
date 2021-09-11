from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class SFPUC_requirement_Demand(BaseParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # Assume 265 MGD = 366.4 MCM/year
        annual_demand_mcm = self.model.parameters["SFPUC requirement/Annual Demand"].value(timestep, scenario_index)

        week = min(timestep.datetime.week, 52)
        daily_fractions = self.model.tables["SFPUC weekly fraction"]
        daily_fraction = daily_fractions[week] / 7
        daily_demand_cms = annual_demand_mcm * daily_fraction / 0.0864

        hh = self.model.nodes["Hetch Hetchy Reservoir"].volume[scenario_index.global_id]
        if hh <= 200:
            demand_reduction = 0.3
            daily_demand_cms *= (1 - demand_reduction)
        else:
            demand_reduction = self.model.parameters["SFPUC requirement/Demand Reduction"].get_value(scenario_index)
            daily_demand_cms *= (1 + demand_reduction / 2)

        return daily_demand_cms

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


SFPUC_requirement_Demand.register()
