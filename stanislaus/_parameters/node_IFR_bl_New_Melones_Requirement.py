import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_New_Melones_Requirement(WaterLPParameter):
    """"""

    annual_ifr = 500  # in the middle somewhere

    def _value(self, timestep, scenario_index):
        if timestep.index == 0:
            # self.inflow = self.read_csv("Scenarios/Livneh/preprocessed/tot_runoff_sbAll.csv", squeeze=True)  # cms
            path = "Management/BAU/IFRs/IFR_Below_Melones_Lake_mcm.csv"
            col_names = ['store_inflow_fr', 'store_inflow_to', 'rel_fr', 'rel_to']
            self.df = self.read_csv(path, usecols=[0, 1, 2, 3], index_col=None, header=0, names=col_names)
            self.runoff_tpl = 'STN_{:02} Headflow/Runoff'
            if self.mode == 'planning':
                self.runoff_tpl += self.month_suffix

        if timestep.month == 3 and timestep.day == 1:
            projected_inflow = 0
            start = timestep.datetime
            end = '{}-09-30'.format(timestep.year)
            for c in range(1, 26):
                projected_inflow += self.model.parameters[self.runoff_tpl.format(c)] \
                                        .dataframe[start:end].sum()

            storage = self.model.nodes["New Melones Lake" + self.month_suffix].volume[-1]
            inflow_plus_storage = projected_inflow + storage
            df = self.df
            r = df[(df['store_inflow_fr'] <= inflow_plus_storage) & (
                    df['store_inflow_to'] > inflow_plus_storage)]
            scale = (r['rel_to'] - r['rel_fr']) / (r['store_inflow_to'] - r['store_inflow_fr'])
            self.annual_ifr = r['rel_fr'] + scale * (inflow_plus_storage - r['store_inflow_fr'])

        ifr_val = self.annual_ifr / 365  # for now

        return ifr_val  # unit: mcm

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


node_IFR_bl_New_Melones_Requirement.register()
print(" [*] node_IFR_bl_New_Melones_Requirement successfully registered")
