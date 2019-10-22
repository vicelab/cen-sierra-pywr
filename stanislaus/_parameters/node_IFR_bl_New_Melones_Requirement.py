import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class node_IFR_bl_New_Melones_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        self.inflow = self.read_csv("Scenarios/Livneh/Runoff/tot_runoff_sbAll.csv", squeeze=True)[timestep.datetime]  # cms
        self.inflow = convert(self.inflow, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        self.storage = self.model.nodes["New Melones Lake [node]"].volume[-1]
        df = self.read_csv("Management/BAU/IFRs/IFR_Below_Melones_Lake_mcm.csv", usecols=[0, 1, 2, 3], index_col=None, header=0,
                             names=['store_inflow_fr', 'store_inflow_to', 'rel_fr', 'rel_to'])
        inflow_store = self.inflow+self.storage
        r = df[(df['store_inflow_fr'] <= inflow_store) & (df['store_inflow_to'] > inflow_store)]
        ifr_val = r['rel_fr']+(((r['rel_to']-r['rel_fr'])/(r['store_inflow_to']-r['store_inflow_fr']))*(inflow_store-r['store_inflow_fr']))
        return ifr_val # unit: mcm

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_IFR_bl_New_Melones_Requirement.register()
print(" [*] node_IFR_bl_New_Melones_Requirement successfully registered")
