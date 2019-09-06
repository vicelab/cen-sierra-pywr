from parameters import WaterLPParameter

from utilities.converter import convert

class node_Shaver_Lake_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        # kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        date_string = timestep.datetime.strftime('%m-%d')
        if date_string >= '12-15' or date_string < '04-01':
            # return self.get("node/Shaver Lake/Inactive Pool", **kwargs) + 50
            return self.model.nodes['Shaver Lake [node]'].min_volume + 50
        else:
            # return self.get("node/Shaver Lake/Storage Capacity", **kwargs)
            return self.model.nodes['Shaver Lake [node]'].max_volume

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Shaver_Lake_Storage_Demand.register()
print(" [*] node_Shaver_Lake_Storage_Demand successfully registered")
