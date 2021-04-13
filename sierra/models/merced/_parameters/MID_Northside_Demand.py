from sierra.base_parameters import WaterLPParameter
from sierra.utilities.converter import convert
from numba import jit, njit, vectorize
from numba.experimental import jitclass

class MID_Northside_Demand(WaterLPParameter):
    """"""

    reductions = [0, 0]

    @jit(fastmath=True)
    def _value(self, timestep, scenario_index):

        WYT = self.model.tables['WYT for IFR Below Exchequer'][self.operational_water_year]
        ts = "{}/{}/1900".format(timestep.month, timestep.day)
        demand_cms = self.model.tables["MID Northside Diversions"].at[ts, WYT] / 35.31

        return demand_cms

    def value(self, timestep, scenario_index):
        return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


MID_Northside_Demand.register()
