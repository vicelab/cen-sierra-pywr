from parameters import WaterLPParameter


class New_Melones_Release_Policy(WaterLPParameter):
    million_m3day_to_m3sec = 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def get_demand(self, timestep, scenario_index):

        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt = self.year_names[wyt_number - 1]
        net_demand = self.read_csv("s3_imports/NetDemand_belowTulloch.csv",
                                   index_col=[0], parse_dates=True)
        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        datestring = '1990-{:02}-{:02}'.format(timestep.month, day)
        return net_demand[wyt][datestring] / self.million_m3day_to_m3sec

    def _value(self, timestep, scenario_index):
        # date_timestep = datetime(1900, timestep.month, timestep.day)
        out_flow = self.model.nodes["New Melones Lake [node]"].volume[-1] \
                   + self.model.nodes["STN_01 Inflow [node]"].flow[-1] \
                   - self.model.parameters["node/New Melones/Storage Demand"].value(timestep, scenario_index)
        base_demand = self.get_demand(timestep, scenario_index)
        ph_demand = self.model.parameters["node/blwTullochPH/Requirement"].value(timestep, scenario_index)
        net_demand = base_demand + ph_demand

        # if datetime(1900, 3, 21) < date_timestep < datetime(1900, 5, 31):
        # Note: datetime not needed since we can compare tuples directly
        month_day = (timestep.month, timestep.day)
        if (3, 12) < month_day < (5, 3):
            # TODO: Add Itot and Dtot logic here
            return max(net_demand, min(out_flow, 226.535))
        elif (8, 1) < month_day < (9, 14):
            return net_demand
        else:
            return max(net_demand, min(out_flow, 226.535))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Release_Policy.register()
print(" [*] New_Melones_Release_Policy successfully registered")
