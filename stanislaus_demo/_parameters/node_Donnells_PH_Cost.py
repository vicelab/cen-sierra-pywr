from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_PH_Cost(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        x = 100 #Value to be adjusted
        path = 'Scenarios/Livneh/energy_netDemand.csv'
        data = self.read_csv(path, usecols=[1,2,3,4], index_col=0, header=None, names=['day','TotDemand','MaxDemand','MinDemand'], parse_dates=False)
        totDemand = data['TotDemand'][timestep.datetime]
        maxDemand= data['MaxDemand'][timestep.datetime]
        minDemand= data['MinDemand'][timestep.datetime]
        minVal = x * (totDemand/768) # 768 GWh is median daily energy demand for 2009
        maxVal = minVal* (maxDemand/minDemand)
        d = maxVal-minVal
        return [-(maxVal-d/8),-(maxVal-3*d/8),-(maxVal-5*d/8),-(maxVal-7*d/8)]
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)
        
node_Donnells_PH_Cost.register()
print(" [*] node_Donnells_PH_Cost successfully registered")
