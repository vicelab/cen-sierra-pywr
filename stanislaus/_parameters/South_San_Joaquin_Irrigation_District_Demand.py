from parameters import WaterLPParameter
from dateutil.relativedelta import relativedelta


class South_San_Joaquin_Irrigation_District_Demand(WaterLPParameter):
    cfs_to_mcm = 1 / 35.31 / 11.5740740741
    year_names = ["Critical", "Dry", "Below", "Above", "Wet"]

    def _value(self, timestep, scenario_index):
        WYT = self.get('San Joaquin Valley WYT' + self.month_suffix)
        wyt_name = self.year_names[WYT - 1]
        demand_cfs = self.read_csv("Management/BAU/Demand/SouthSanJoaquin_IrrigationDistrict_Demand_cfs.csv",
                                   index_col=[0], parse_dates=False)
        if self.model.mode == 'scheduling':
            demand_mcm = demand_cfs[wyt_name][self.datetime.strftime('%b-%d')] * self.cfs_to_mcm
        else:
            start = self.datetime.strftime('%b-%d')
            end = (self.datetime + relativedelta(days=+self.days_in_month()-1)).strftime('%b-%d')
            demand_mcm = demand_cfs[wyt_name][start:end].sum() * self.cfs_to_mcm
        return demand_mcm

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
