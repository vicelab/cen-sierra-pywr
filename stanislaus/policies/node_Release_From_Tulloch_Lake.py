from parameters import WaterLPParameter

class node_Release_From_Tulloch_Lake(WaterLPParameter):
    million_m3day_to_m3sec = 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def get_demand(self, timestep, scenario_index):

        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt = self.year_names[wyt_number-1]
        net_demand = self.read_csv("NetDemand_belowTulloch.csv", index_col=[0], parse_dates=True)

        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        datestring = '1990-{:02}-{:02}'.format(timestep.month, day)
        return net_demand[wyt][datestring] / self.million_m3day_to_m3sec

    def _value(self, timestep, scenario_index):
        max_outflow = 226.535
        # Reservoir Node (Tulloch)
        storage_name = "Tulloch Lake [node]" + self.month_suffix
        storage_demand_name = "node/Tulloch Lake/Storage Demand"
        # Inflow into Tulloch Lake
        inflow_name = "STN_below_Melons.2.2" + self.month_suffix
        outflow = self.model.nodes[storage_name].volume[-1] \
                  + self.model.nodes[inflow_name].flow[-1] \
                  - self.model.parameters[storage_demand_name].value(timestep, scenario_index)

        tulloch_reqt_name = "node/blwTullochPH/Requirement" + self.month_suffix
        net_demand = self.get_demand(timestep, scenario_index) \
                     + self.model.parameters[tulloch_reqt_name].value(timestep, scenario_index)
        return max(net_demand, min(outflow, max_outflow))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Release_From_Tulloch_Lake.register()
print(" [*] node_Release_From_Tulloch_Lake successfully registered")
