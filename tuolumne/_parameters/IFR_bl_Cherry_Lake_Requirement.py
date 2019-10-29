from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Cherry_Lake_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        if timestep.month in [7,8,9]:
            ifr = 15.5
        else:
            ifr = 5
        
        return ifr*2 / 35.31 # Note: SFPUC releases twice the requirement for surety
        
    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Cherry_Lake_Requirement.register()
print(" [*] IFR_bl_Cherry_Lake_Requirement successfully registered")
