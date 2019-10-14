from parameters import WaterLPParameter

from utilities.converter import convert


class WYI_SJValley(WaterLPParameter):
    """"""

    def value(self, timestep, scenario_index):
        sjvi = self.read_csv("Scenarios/Livneh/WYT/SJVI.csv", parse_dates=False, squeeze=True)
        water_year = timestep.year if timestep.month < 10 else timestep.year + 1
        print(water_year)
        return sjvi[water_year]

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


WYI_SJValley.register()
print(" [*] WYI_SJValley successfully registered")
