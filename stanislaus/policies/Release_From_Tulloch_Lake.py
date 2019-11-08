from parameters import WaterLPParameter


class Release_From_Tulloch_Lake(WaterLPParameter):
    cms_to_mcm = 1 / 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def _value(self, timestep, scenario_index):
        # max_outflow = 226.535
        #
        # # anticipated outflow
        # prev_storage = self.model.nodes["Tulloch Lake" + self.month_suffix].volume[-1]
        # prev_inflow = self.model.nodes["STN_below_Melons.2.2" + self.month_suffix].flow[-1]
        # storage_demand = self.model.parameters["Tulloch Lake/Storage Demand"].value(timestep, scenario_index)
        # outflow = prev_storage + prev_inflow - storage_demand
        #
        # # net demand
        # reqt = self.model.parameters["IFR bl Goodwin Reservoir/Requirement" + self.month_suffix].value(timestep, scenario_index)
        #
        # net_demand = self.model.parameters["Oakdale Irrigation District/Demand"].value(timestep, scenario_index) \
        #     + self.model.parameters["South San Joaquin Irrigation District/Demand"].value(timestep, scenario_index)
        #
        # total_demand = net_demand + reqt
        #
        # return max(total_demand, min(outflow, max_outflow))
        return 0.0

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


Release_From_Tulloch_Lake.register()
print(" [*] Release_From_Tulloch_Lake successfully registered")
