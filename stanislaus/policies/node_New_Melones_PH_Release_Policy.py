from parameters import WaterLPParameter


flow_threshold = 19.572
class New_Melones_Release_Policy(WaterLPParameter):
    million_m3day_to_m3sec = 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def get_demand(self, timestep, scenario_index):

        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt = self.year_names[wyt_number - 1]
        net_demand = self.read_csv("NetDemand_belowTulloch.csv",
                                   index_col=[0], parse_dates=True)
        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        datestring = '1990-{:02}-{:02}'.format(timestep.month, day)
        return net_demand[wyt][datestring] / self.million_m3day_to_m3sec

    def _value(self, timestep, scenario_index):
        # date_timestep = datetime(1900, timestep.month, timestep.day)
        storage_name = "New Melones Lake [node]" + self.month_suffix
        inflow_name = "STN_01 Inflow [node]" + self.month_suffix
        outflow = self.model.nodes[storage_name].volume[-1] \
                   + self.model.nodes[inflow_name].flow[-1] \
                   - self.model.parameters["node/New Melones Lake/Storage Demand"].value(timestep, scenario_index)
        base_demand = self.get_demand(timestep, scenario_index)
        ph_demand = self.model.parameters["node/blwTullochPH/Requirement" + self.month_suffix].value(timestep, scenario_index)
        net_demand = base_demand + ph_demand

        # if datetime(1900, 3, 21) < date_timestep < datetime(1900, 5, 31):
        # Note: datetime not needed since we can compare tuples directly
        month_day = (timestep.month, timestep.day)
        if (3, 12) < month_day < (5, 3):
            # TODO: Add Itot and Dtot logic here
            return max(net_demand, min(outflow, 226.535))
        elif (8, 1) < month_day < (9, 14):
            return net_demand
        else:
            return max(net_demand, min(out_flow, flow_threshold))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Release_Policy.register()
print(" [*] New_Melones_Release_Policy successfully registered")
