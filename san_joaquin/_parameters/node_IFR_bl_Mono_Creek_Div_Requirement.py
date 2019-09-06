from parameters import WaterLPParameter

from utilities.converter import convert

class node_IFR_bl_Mono_Creek_Div_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        management = 'BAU'
        path = "Management/{mgt}/IFRs/IFRblMonoCreekDiv.csv".format(mgt=management)
        ifr = self.read_csv(path, index_col=0, skiprows=1, header=None, parse_dates=False)
        WYT = self.model.parameters['WYT_SJValley'].value(timestep, scenario_index)
        week = min(timestep.datetime.weekofyear, 52)
        return ifr[WYT][week] / 35.31
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_IFR_bl_Mono_Creek_Div_Requirement.register()
print(" [*] node_IFR_bl_Mono_Creek_Div_Requirement successfully registered")
