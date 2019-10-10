from parameters import WaterLPParameter

from utilities.converter import convert


class network_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        month_offset = 0
        if self.mode == 'scheduling':
            res_class, res_name, attr_name = self.name.split('/')
        else:  # planning mode
            res_class, res_name, attr_name, month = self.name.split('/')
            month_offset = int(month) - 1

        nblocks = 4  # we can set this up as a variable
        qDemand = self.model.parameters['node/' + res_name + '/Turbine Capacity']\
            .value(timestep, scenario_index) * 3600 * 24 / nblocks

        if self.mode == 'planning':
            qDemand *= self.days_in_planning_month(timestep, month_offset=month_offset)

        return qDemand

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index) / 1e6

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


network_PH_Water_Demand.register()
print(" [*] network_PH_Water_Demand successfully registered")
