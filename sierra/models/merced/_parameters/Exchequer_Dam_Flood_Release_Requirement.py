from sierra.base_parameters import BaseParameter
from scipy import interpolate
from sierra.utilities.converter import convert


class Exchequer_Dam_Flood_Release_Requirement(BaseParameter):
    """
    This policy calculates release from Exchequer Dam.
    """

    esrd_spline = None

    zones = {
        (1, 1): 247.311672,
        (3, 15): 247.311672,
        (6, 15): 264.97788,
        (6, 30): 264.97788,
        (7, 31): 262.89,
        (8, 31): 259.2324,
        (9, 30): 252.984,
        (10, 31): 247.311672
    }  # Units - meters

    wyt = 'normal'

    max_release_cms = 6500 / 35.315  # 6500 cfs

    def setup(self):
        super().setup()

        table = self.model.tables["Lake McClure Spill/ESRD"]
        rows = table.iloc[1:, 0]
        cols = table.iloc[0, 1:]
        values = table.values[1:, 1:]
        self.esrd_spline = interpolate.RectBivariateSpline(rows, cols, values, kx=1, ky=1)

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

        # FLOOD RELEASE

        date_str = '1900-{:02}-{:02}'.format(timestep.month, timestep.day)
        target_mcm = self.model.tables["Lake McClure/Guide Curve"].at[date_str, self.wyt] * 1233.5 / 1e6
        curr_inflow = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)
        lake_mcclure_volume = self.model.nodes["Lake McClure"].volume[scenario_index.global_id]
        flood_release_mcm = lake_mcclure_volume + curr_inflow - target_mcm
        flood_release_cms = max(flood_release_mcm, 0.0) / 0.0864

        # ESRD

        esrd_release_cms = 0.0

        if elevation >= 255.83388:
            curr_inflow_mcm = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index)  # mcm/day
            curr_inflow_cms = curr_inflow_mcm / 0.0864  # Convert mcm/day to cms
            esrd_release_cms = self.esrd_spline(elevation, curr_inflow_cms)

        is_conservation_zone = False
        month_day = (timestep.month, timestep.day)
        # Floor function for the entries in the dict. Looks for the first value that is greater than our given date
        # Which means the dict value we are looking for is the one before.
        for month_day_key, zone_value in self.zones.items():
            if month_day <= month_day_key:
                is_conservation_zone = elevation > zone_value
                break

        release_cms = 0.0
        if is_conservation_zone and elevation <= 264.9779:  # Between conservation zone and 869.35 ft
            release_cms = min(esrd_release_cms, self.max_release_cms)  # Min of ESRD release or 6500 cfs
        elif 264.9779 < elevation < 269.4432:  # Between 869.35 ft and 884 ft
            release_cms = esrd_release_cms  # ESRD release in cms

        flood_release_cms = min(flood_release_cms, self.max_release_cms)
        release_cms = max(release_cms, flood_release_cms)

        return release_cms

    def value(self, timestep, scenario_index):
        val = self._value(timestep, scenario_index)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Exchequer_Dam_Flood_Release_Requirement.register()
