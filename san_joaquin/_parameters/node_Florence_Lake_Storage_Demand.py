from parameters import WaterLPParameter

from utilities.converter import convert

class node_Florence_Lake_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        # kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        #date1 = pendulum.datetime(water_year-1, 12, 15) #Dec 15
        #date2 = pendulum.datetime(water_year, 4, 1) # Apr 1
        #if date1 <= date <= date2:
        #    return self.get("node/Florence Lake/Inactive Pool", **kwargs)
        #else:
        #    return self.get("node/Florence Lake/Storage Capacity", **kwargs)
        # return self.get("node/Florence Lake/Storage Capacity", **kwargs)
        return self.model.nodes['Florence Lake [node]'].max_volume
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Florence_Lake_Storage_Demand.register()
print(" [*] node_Florence_Lake_Storage_Demand successfully registered")
