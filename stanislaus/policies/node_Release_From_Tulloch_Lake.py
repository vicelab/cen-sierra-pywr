from parameters import WaterLPParameter

class node_Release_From_Tulloch_Lake(WaterLPParameter):
    million_m3day_to_m3sec = 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def get_demand(self, timestep, scenario_index):

        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt = self.year_names[wyt_number-1]
        net_demand = self.read_csv("s3_imports/NetDemand_belowTulloch.csv", index_col=[0], parse_dates=True)

        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        datestring = '1990-{:02}-{:02}'.format(timestep.month, day)
        return net_demand[wyt][datestring] / self.million_m3day_to_m3sec

    def _value(self, timestep, scenario_index):
        out_flow = self.model.nodes["Tulloch Lake [node]"].volume[-1] + self.model.nodes["STN_below_Melons.2.2"].flow[-1] - self.model.parameters["node/Tulloch Lake/Storage Demand"].value(timestep, scenario_index)
        net_demand = self.get_demand(timestep, scenario_index) + self.model.parameters["node/blwTullochPH/Requirement"].value(timestep, scenario_index)
        return max(net_demand, min(out_flow, 226.535))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Release_From_Tulloch_Lake.register()
print(" [*] node_Release_From_Tulloch_Lake successfully registered")
