from parameters import WaterLPParameter


class node_Release_From_Tulloch_Lake(WaterLPParameter):
    million_m3day_to_m3sec = 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def get_demand(self, timestep, scenario_index):

        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt = self.year_names[wyt_number - 1]
        net_demand = self.read_csv("Management/BAU/NetDemand_belowTulloch.csv", index_col=[0], parse_dates=True)

        day = timestep.day if timestep.month != 2 else min(28, timestep.day)
        datestring = '1990-{:02}-{:02}'.format(timestep.month, day)
        return net_demand[wyt][datestring] / self.million_m3day_to_m3sec

    def _value(self, timestep, scenario_index):
        max_outflow = 226.535

        # anticipated outflow
        prev_storage = self.model.nodes["Tulloch Lake" + self.month_suffix].volume[-1]
        prev_inflow = self.model.nodes["STN_below_Melons.2.2" + self.month_suffix].flow[-1]
        storage_demand = self.model.parameters["Tulloch Lake/Storage Demand"].value(timestep, scenario_index)
        outflow = prev_storage + prev_inflow - storage_demand

        # net demand
        reqt = self.model.parameters["IFR below Goodwin Reservoir/Requirement" + self.month_suffix].value(timestep, scenario_index)
        net_demand = self.get_demand(timestep, scenario_index) + reqt

        return max(net_demand, min(outflow, max_outflow))

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Release_From_Tulloch_Lake.register()
print(" [*] node_Release_From_Tulloch_Lake successfully registered")
