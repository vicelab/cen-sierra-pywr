import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_New_Melones_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        if timestep.index == 0:
            # self.inflow = self.read_csv("Scenarios/Livneh/preprocessed/tot_runoff_sbAll.csv", squeeze=True)  # cms
            path = "Management/BAU/IFRs/IFR_Below_Melones_Lake_mcm.csv"
            col_names = ['store_inflow_fr', 'store_inflow_to', 'rel_fr', 'rel_to']
            self.df = self.read_csv(path, usecols=[0, 1, 2, 3], index_col=None, header=0, names=col_names)
            self.runoff_tpl = 'STN_{:02} Headflow/Runoff'
            if self.mode == 'planning':
                self.runoff_tpl += self.month_suffix
        # inflow = self.model.parameters["Total Runoff"].value(timestep, scenario_index)
        # on-the-fly summing of runoff doesn't seem particularly slow

        inflow = sum(
            [self.model.parameters[self.runoff_tpl.format(c)].value(timestep, scenario_index)
             for c in range(1, 26)]
        )
        inflow = convert(inflow, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        storage = self.model.nodes["New Melones Lake" + self.month_suffix].volume[-1]
        inflow_store = inflow + storage
        df = self.df
        r = df[(df['store_inflow_fr'] <= inflow_store) & (df['store_inflow_to'] > inflow_store)]
        ifr_val = r['rel_fr'] + (((r['rel_to'] - r['rel_fr']) / (r['store_inflow_to'] - r['store_inflow_fr'])) * (
                inflow_store - r['store_inflow_fr']))
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
