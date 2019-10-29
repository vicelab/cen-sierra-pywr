from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Lake_Eleanor_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        schedule = self.model.parameters["IFR bl Lake Eleanor/IFR Schedule"].array()
        
        is_pumping = True
        
        # convert the schedule to a dictionary to lookup values
        ifr_lookup = {row[0]: row[1:] for row in schedule[1:]}
        
        month_name = date.format("MMMM") # e.g., "January"
        if date.month in [4, 9]:
            ifr_period = '{}_{}'.format(month_name, date.day)
        else:
            ifr_period = month_name
        
        ifr = ifr_lookup[ifr_period][0 if is_pumping else 1]
        
        return ifr
        
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
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Lake_Eleanor_Requirement.register()
print(" [*] IFR_bl_Lake_Eleanor_Requirement successfully registered")
