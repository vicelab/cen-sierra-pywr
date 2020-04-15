from parameters import WaterLPParameter
from datetime import datetime, timedelta
from scipy import interpolate
import numpy as np


class Exchequer_Dam_Flood_Release_Requirement(WaterLPParameter):
    """
    This policy calculates release from Exchequer Dam.
    """

    esrd_spline = None
    zones = None
    wyt = 'normal'

    def setup(self):
        super().setup()

        table = self.model.tables["Lake McClure Spill/ESRD"]
        rows = table.iloc[1:, 0]
        cols = table.iloc[0, 1:]
        values = table.values[1:, 1:]
        self.esrd_spline = interpolate.RectBivariateSpline(rows, cols, values, kx=1, ky=1)

        self.zones = {
            (1, 1): 247.311672,
            (3, 15): 247.311672,
            (6, 15): 264.97788,
            (6, 30): 264.97788,
            (7, 31): 262.89,
            (8, 31): 259.2324,
            (9, 30): 252.984,
            (10, 31): 247.311672
        }  # Units - meters

    def before(self):
        super().before()
        if (self.model.timestep.month, self.model.timestep.day) == (10, 1):
            SJVI = self.model.tables["San Joaquin Valley Index"][self.model.timestep.year + 1]
            if SJVI <= 2.5:
                self.wyt = 'dry'
            elif SJVI < 3.8:
                self.wyt = 'normal'
            else:
                self.wyt = 'wet'

    def _value(self, timestep, scenario_index):

        elevation = self.model.parameters["Lake McClure/Elevation"].value(timestep, scenario_index)

        return_value = 0.0

        # ESRD

        esrd = 0.0

        if elevation >= 255.83388:
            curr_inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)  # mcm/day
            curr_inflow *= 11.57407  # Convert mcm/day to cms
            esrd = self.esrd_spline(elevation, curr_inflow)

        is_conservation_zone = False
        month_day = (timestep.month, timestep.day)
        # Floor function for the entries in the dict. Looks for the first value that is greater than our given date
        # Which means the dict value we are looking for is the one before.
        for month_day_key, zone_value in self.zones.items():
            if month_day <= month_day_key:
                is_conservation_zone = elevation > zone_value
                break

        if is_conservation_zone and elevation <= 264.9779:  # Between conservation zone and 869.35 ft
            return_value = min(esrd, 169.901082)  # Min of ESRD release or 6500 cfs
        elif 264.9779 < elevation < 269.4432:  # Between 869.35 ft and 884 ft
            return_value = esrd  # ESRD release in cms

        return_value /= 11.57407  # Convert cms to mcm/day

        # FLOOD RELEASE

        date_str = '1900-{:02}-{:02}'.format(timestep.month, timestep.day)
        target_mcm = self.model.tables["Lake McClure/Guide Curve"].at[date_str, self.wyt] * 1233.5 / 1e6
        curr_inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)
        lake_mcclure_volume = self.model.nodes["Lake McClure"].volume[scenario_index.global_id]
        flood_release = lake_mcclure_volume + curr_inflow - target_mcm

        return max(return_value, flood_release)

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Exchequer_Dam_Flood_Release_Requirement.register()
