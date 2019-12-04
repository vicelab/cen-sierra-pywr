from parameters import WaterLPParameter

from utilities.converter import convert

class Lake_McClure_Observed_Storage(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        return self.read_csv("Observed/Reservoirs/GaugeReservoir_mcm_MERR.csv", header=0, index_col=0, parse_dates=True)["Lake McClure"][timestep.datetime]
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
Lake_McClure_Observed_Storage.register()
print(" [*] Lake_McClure_Observed_Storage successfully registered")
