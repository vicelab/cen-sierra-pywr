from parameters import WaterLPParameter

from utilities.converter import convert

class node_MERCED_R_A_POHONO_BRIDGE_NR_YOSEMITE_CA_11266500_Observed_Flow(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        return 5
        # path="{LocalDir}/GAGES/USGS_11266500.csv".format(LocalDir=self.GET("network/1156/1597", **kwargs))
        # data = self.read_csv(path, usecols=[0,1,2], comment=';', header=None, **kwargs)
        # return data.iloc[timestep][2]*self.GET("cfs2cms", **kwargs)
        
    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_MERCED_R_A_POHONO_BRIDGE_NR_YOSEMITE_CA_11266500_Observed_Flow.register()
print(" [*] node_MERCED_R_A_POHONO_BRIDGE_NR_YOSEMITE_CA_11266500_Observed_Flow successfully registered")
