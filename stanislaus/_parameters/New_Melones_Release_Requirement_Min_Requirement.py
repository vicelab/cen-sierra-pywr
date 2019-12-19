import datetime
from parameters import WaterLPParameter

from utilities.converter import convert


class New_Melones_Release_Requirement_Min_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # IFR req't
        reqt_cms = self.get("IFR bl Goodwin Reservoir/Requirement" + self.month_suffix) / 0.0864  # mcm to cms

        # Flood release below Tulloch
        # reqt_cms += self.get("Lake Tulloch Flood Control/Requirement" + self.month_suffix) / 0.0864  # mcm to cms

        SSJID = self.get("South San Joaquin Irrigation District/Demand" + self.month_suffix) / 0.0864  # mcm to cms
        OID = self.get("Oakdale Irrigation District/Demand" + self.month_suffix) / 0.0864  # mcm to cms
        reqt_cms += SSJID + OID

        # additional release for filling Tulloch during the refill period
        if (3, 21) <= (self.datetime.month, self.datetime.day) <= (5, 30):
            # release to Tulloch = (Smax - Smin) / refill days (approx. 68)
            reqt_cms += 12.33 / 68 / 0.0864  # mcm to cms

        return reqt_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


New_Melones_Release_Requirement_Min_Requirement.register()
print(" [*] New_Melones_Release_Requirement_Min_Requirement successfully registered")
