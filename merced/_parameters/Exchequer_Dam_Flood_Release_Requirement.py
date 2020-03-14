from parameters import WaterLPParameter
from datetime import datetime, timedelta
from scipy import interpolate
import numpy as np


class Exchequer_Dam_Flood_Release_Requirement(WaterLPParameter):
    """
    This policy calculates release from Exchequer Dam.
    """

    def _value(self, timestep, scenario_index):

        if timestep.index == 0:
            table = self.model.tables["Lake McClure Spill/ESRD"]
            rows = table.iloc[1:, 0]
            cols = table.iloc[0, 1:]
            values = table.values[1:, 1:]
            self.esrd_spline = interpolate.RectBivariateSpline(rows, cols, values, kx=1, ky=1)
        self.elevation = self.model.parameters["Lake McClure/Elevation"].value(timestep, scenario_index)

        return_value = 0

        if self.is_conservation_zone(timestep, scenario_index, ">") and self.elevation <= 264.9779:  # Between conservation zone and 869.35 ft
            return_value = self.flood_control(timestep, scenario_index) #cms

        elif self.elevation < 264.9779 and self.elevation < 269.4432:  # Between 869.35 ft and 884 ft
            return_value = self.surcharge(timestep, scenario_index) #cms

        return_value = return_value/11.57407 #Convert cms to mcm/day
        return max(return_value, self.flood_release(timestep, scenario_index))

    def value(self, timestep, scenario_index):
        return self._value(timestep, scenario_index)

    def get_esrd(self, timestep, scenario_index):
        if self.elevation < 255.83388:
            return 0

        curr_inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index) #mcm/day
        curr_inflow = curr_inflow * 11.57407 #Convert mcm/day to cms
        return self.esrd_spline(self.elevation, curr_inflow)

    def is_conservation_zone(self, timestep, scenario_index, operation):
        zones = {datetime(2000, 1, 1): 247.311672, datetime(2000, 3, 15): 247.311672, datetime(2000, 6, 15): 264.97788,
                 datetime(2000, 6, 30): 264.97788, datetime(2000, 7, 31): 262.89, datetime(2000, 8, 31): 259.2324,
                 datetime(2000, 9, 30): 252.984, datetime(2000, 10, 31): 247.311672}  # Units - meters
        date = datetime(2000, timestep.month, timestep.day)

        for index in range(0, len(zones.keys())):
            list_zones = list(zones.keys())
            # Floor function for the entries in the dict. Looks for the first value that is greater than our given date
            # Which means the dict value we are looking for is the one before.
            if date <= list_zones[index]:
                zone_value = zones[list_zones[index-1]]
                if operation == "<":
                    return self.elevation < zone_value
                elif operation == ">":
                    return self.elevation > zone_value
                else:
                    raise TypeError("Invalid Operation Input")
        return False

    def flood_control(self, timestep, scenario_index):
        return min(self.get_esrd(timestep, scenario_index), 169.901082)  # Min of ESRD release or 6500 cfs

    def surcharge(self, timestep, scenario_index):
        return self.get_esrd(timestep, scenario_index)  # ESRD release


    def flood_release(self, timestep, scenario_index):
        if (timestep.month, timestep.day) == (10, 1):
            SJVI = self.model.tables["San Joaquin Valley Index"][timestep.year + 1]

            if SJVI <= 2.5:
                self.wyt = 'dry'
            elif SJVI < 3.8:
                self.wyt = 'normal'
            else:
                self.wyt = 'wet'

        curves_af = self.model.tables["Lake McClure/Guide Curve"]
        date_str = '1900-{:02}-{:02}'.format(timestep.month, timestep.day)
        target_mcm = curves_af.at[date_str, self.wyt] * 1233.5 / 1e6

        curr_inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)

        return (self.model.nodes["Lake McClure"].volume[scenario_index.global_id] +curr_inflow)-target_mcm

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Exchequer_Dam_Flood_Release_Requirement.register()
print(" [*] Exchequer_Dam_Flood_Release_Requirement successfully registered")