from parameters import WaterLPParameter

from utilities.converter import convert


class MID_Main_Demand(WaterLPParameter):
    """"""

    reductions = [0, 0]

    def _value(self, timestep, scenario_index):
        m3_to_cfs = 35.31
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

        demand_cms = self.model.tables["MID Main Diversions"].at[ts, year_type] / 35.31

        idx = scenario_index.indices[1]
        reduction = 0.0
        if idx == 1:
            ifr_param = self.model.parameters["IFR bl Crocker-Huffman Dam/Requirement"]
            reduction = ifr_param.swrcb_levels[scenario_index.indices[0]]

        demand_cms *= (1 - reduction)
        return demand_cms

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


MID_Main_Demand.register()
print(" [*] MID_Main_Demand successfully registered")
