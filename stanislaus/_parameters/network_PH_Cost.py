from parameters import WaterLPParameter


class network_PH_Cost(WaterLPParameter):
    """"""

    # path = "s3_imports/energy_netDemand.csv"

    def _value(self, timestep, scenario_index):
        res_class, res_name, attr_name, piece = self.name.split('/')

        Dtot = self.model.parameters["Total Net Energy Demand"].value(timestep, scenario_index)
        Dmax = self.model.parameters["Max Net Energy Demand"].value(timestep, scenario_index)
        Dmin = self.model.parameters["Min Net Energy Demand"].value(timestep, scenario_index)

        # data = self.read_csv(self.path, index_col=0, parse_dates=True)
        # totDemand, maxDemand, minDemand = data.loc[timestep.datetime]
        param_name = "node/" + res_name + "/Demand Constant"
        dem = self.model.parameters[param_name].value(timestep, scenario_index)
        Vmin = dem * (Dtot / 768)  # 768 GWh is median daily energy demand for 2009
        Vmax = Vmin * (Dmax / Dmin)
        return -(Vmax - (int(piece) * 2 - 1) * (Vmax - Vmin) / 8)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)

network_PH_Cost.register()

print(" [*] PH_Cost successfully registered")
