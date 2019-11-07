import datetime
from parameters import WaterLPParameter
from utilities.converter import convert

class node_IFR_below_Beardsley_Afterbay_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        WYT = int(self.get("WYI_SJValley"))
        if (WYT == 1|WYT ==2):
            ifr_val = 50
        else:
            ifr_val = 135
        if self.mode == 'planning':
            ifr_val *= self.days_in_month()
        return ifr_val/35.314666


    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)


    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


node_IFR_below_Beardsley_Afterbay_Requirement.register()
print(" [*] node_IFR_below_Beardsley_Afterbay_Requirement successfully registered")
