import pandas as pd
from parameters import WaterLPParameter

from utilities.converter import convert

class node_Donnells_PH_Cost_1(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        path = "s3_imports/energy_netDemand.csv"
        data = pd.read_csv(path, header=None, index_col=0,names=['day', 'TotDemand', 'MaxDemand', 'MinDemand'])
        totDemand = float(data['TotDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        maxDemand = float(data['MaxDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minDemand = float(data['MinDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minVal = self.model.parameters["node/Donnells PH/Demand Constant"].value(timestep, scenario_index) * (totDemand/768) # 768 GWh is median daily energy demand for 2009
        maxVal = minVal* (maxDemand/minDemand)
        d = maxVal-minVal
        return -(maxVal-d/8)
        
    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


class node_Donnells_PH_Cost_2(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        path = "s3_imports/energy_netDemand.csv"
        data = pd.read_csv(path, header=None, index_col=0,names=['day', 'TotDemand', 'MaxDemand', 'MinDemand'])
        totDemand = float(data['TotDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        maxDemand = float(data['MaxDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minDemand = float(data['MinDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minVal = self.model.parameters["node/Donnells PH/Demand Constant"].value(timestep, scenario_index) * (
                    totDemand / 768)  # 768 GWh is median daily energy demand for 2009
        maxVal = minVal * (maxDemand / minDemand)
        d = maxVal - minVal
        return -(maxVal-3*d/8)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


class node_Donnells_PH_Cost_3(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        path = "s3_imports/energy_netDemand.csv"
        data = pd.read_csv(path, header=None, index_col=0,names=['day', 'TotDemand', 'MaxDemand', 'MinDemand'])
        totDemand = float(data['TotDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        maxDemand = float(data['MaxDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minDemand = float(data['MinDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minVal = self.model.parameters["node/Donnells PH/Demand Constant"].value(timestep, scenario_index) * (
                    totDemand / 768)  # 768 GWh is median daily energy demand for 2009
        maxVal = minVal * (maxDemand / minDemand)
        d = maxVal - minVal
        return -(maxVal-5*d/8)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


class node_Donnells_PH_Cost_4(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        path = "s3_imports/energy_netDemand.csv"
        data = pd.read_csv(path, header=None, index_col=0,names=['day', 'TotDemand', 'MaxDemand', 'MinDemand'])
        totDemand = float(data['TotDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        maxDemand = float(data['MaxDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minDemand = float(data['MinDemand'][str(timestep.month) + "/" + str(timestep.day) + "/" + str(timestep.year)])
        minVal = self.model.parameters["node/Donnells PH/Demand Constant"].value(timestep, scenario_index) * (
                    totDemand / 768)  # 768 GWh is median daily energy demand for 2009
        maxVal = minVal * (maxDemand / minDemand)
        d = maxVal - minVal
        return -(maxVal-7*d/8)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_Donnells_PH_Cost_1.register()
node_Donnells_PH_Cost_2.register()
node_Donnells_PH_Cost_3.register()
node_Donnells_PH_Cost_4.register()

print(" [*] node_Donnells_PH_Cost successfully registered")
