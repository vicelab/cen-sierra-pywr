from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_McClure_Storage_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # read the San Joaquin Index
        if timestep.index == 0:
            self.curves = self.read_csv("policies/LakeMcLure_FloodControl_Requirements.csv",
                                        names=['date', 'dry', 'normal', 'wet'],
                                        index_col=0, parse_dates=False, header=0)
            # self.curves *= 1233.5 / 1e6 / 1294 # convert to million cubic meters
            self.curves /= 1.049e6 # normalize by AF
            self.SJVI = self.model.tables["San Joaquin Valley Index"]
          
        if (timestep.month, timestep.day) == (10, 1):
            SJVI = self.SJVI[timestep.year + 1]
        
            if SJVI <= 2.5:
                self.wyt = 'dry'
            elif SJVI < 3.8:
                self.wyt = 'normal'
            else:
                self.wyt = 'wet'
        
        date_str = '1900-{:02}-{:02}'.format(timestep.month, timestep.day)
        val = self.curves[self.wyt][date_str]
        return val
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
Lake_McClure_Storage_Demand.register()
print(" [*] Lake_McClure_Storage_Demand successfully registered")
