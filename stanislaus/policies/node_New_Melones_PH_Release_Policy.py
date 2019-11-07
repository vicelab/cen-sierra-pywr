from parameters import WaterLPParameter


class New_Melones_Release_Policy(WaterLPParameter):
    cms_to_mcm = 1 / 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]
    flow_threshold = 19.572

    def _value(self, timestep, scenario_index):
        # date_timestep = datetime(1900, timestep.month, timestep.day)
        # storage_name = "New Melones Lake" + self.month_suffix
        # inflow_name = "STN_01 Inflow" + self.month_suffix
        # outflow = self.model.nodes[storage_name].volume[-1] \
        #           + self.model.nodes[inflow_name].flow[-1] \
        #           - self.model.parameters["New Melones Lake/Storage Demand"].value(timestep, scenario_index)
        #
        # # net demand
        # net_demand = self.model.parameters["Oakdale Irrigation District/Demand"].value(timestep, scenario_index) \
        #     + self.model.parameters["South San Joaquin Irrigation District/Demand"].value(timestep, scenario_index)
        # ph_demand = self.model.parameters["IFR bl Goodwin Reservoir/Requirement" + self.month_suffix].value(timestep,
        #                                                                                                        scenario_index)
        # total_demand = net_demand + ph_demand
        #
        # # if datetime(1900, 3, 21) < date_timestep < datetime(1900, 5, 31):
        # # Note: datetime not needed since we can compare tuples directly
        # month_day = (timestep.month, timestep.day)
        # if (3, 12) < month_day < (5, 3):
        #     # TODO: Add Itot and Dtot logic here
        #     return max(total_demand, min(outflow, 226.535))
        # elif (8, 1) < month_day < (9, 14):
        #     return total_demand
        # else:
        #     return max(total_demand, min(outflow, self.flow_threshold))
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


New_Melones_Release_Policy.register()
print(" [*] New_Melones_Release_Policy successfully registered")
