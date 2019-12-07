from parameters import WaterLPParameter

from utilities.converter import convert


class MID_Northside_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        type_value = self.model.tables['WYT for IFR Below Exchequer'][timestep.year]
        ts = "{}/{}/1900".format(timestep.month, timestep.day)

        if type_value == 1:
            year_type = "Critical"
        elif type_value == 2:
            year_type = "Dry"
        elif type_value == 3:
            year_type = "Below"
        elif type_value == 4:
            year_type = "Above"
        else:
            year_type = "Wet"

        return self.model.tables["MID Diversions"].at[ts, year_type] / 35.31

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


MID_Northside_Demand.register()
print(" [*] MID_Northside_Demand successfully registered")
