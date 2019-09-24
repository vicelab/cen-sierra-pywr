from parameters import WaterLPParameter

from utilities.converter import convert

class node_Spring_Gap_PH_Water_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        TC = self.model.parameters["node/Spring Gap PH/Turbine Capacity"].value(timestep, scenario_index)
        qDemand = TC * 3600 * 6
        return qDemand

    def value(self, timestep, scenario_index):
        m3day_to_millionm3 = 0.000001
        return self._value(timestep, scenario_index) * m3day_to_millionm3

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Spring_Gap_PH_Water_Demand.register()
print(" [*] node_Spring_Gap_PH_Water_Demand successfully registered")
