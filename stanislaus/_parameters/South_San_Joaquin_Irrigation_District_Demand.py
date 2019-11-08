from parameters import WaterLPParameter


class South_San_Joaquin_Irrigation_District_Demand(WaterLPParameter):
    cfs_to_mcm = 1 / 35.31 / 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def _value(self, timestep, scenario_index):
        wyt_number = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        wyt_name = self.year_names[wyt_number - 1]
        demand_cms_df = self.read_csv("Management/BAU/Demand/SouthSanJoaquin_IrrigationDistrict_Demand_cfs.csv",
                                      index_col=[0], parse_dates=False)
        demand_cms = demand_cms_df.at[timestep.datetime.strftime('%b-%d'), wyt_name]
        return demand_cms * self.cfs_to_mcm

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


South_San_Joaquin_Irrigation_District_Demand.register()
print(" [*] South_San_Joaquin_Irrigation_District_Demand successfully registered")
