from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Kerckhoff_Lake_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        management = 'BAU'
        path = "Management/{mgt}/IFRs/IFRblKerckhoffLake.csv".format(mgt=management)
        data = self.read_csv(path, usecols=[0,1,2,3,4,5], index_col=0, header=None, names=['week','1','2','3','4','5'], parse_dates=False)
        WYT = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        week = min(timestep.datetime.weekofyear, 52)
        ifr = data[str(WYT)][week]
        return convert(ifr, 'ft^3 s^-1', 'hm^3 day^-1')
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Kerckhoff_Lake_Requirement.register()
print(" [*] node_IFR_bl_Kerckhoff_Lake_Requirement successfully registered")
