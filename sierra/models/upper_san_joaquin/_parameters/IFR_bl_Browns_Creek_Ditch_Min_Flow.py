from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert

class IFR_bl_Browns_Creek_Ditch_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        # Get Year Type
        year_type = self.model.parameters["San Joaquin Valley WYT" + self.month_suffix].value(timestep, scenario_index)
        
        if year_type in [1,2]:  # Critical or Dry WYT
            return_val = 3
            if self.model.mode == "planning":
                return_val *= self.days_in_month
            return return_val
        
        # Get month
        month = self.datetime.month
        prescribed = 0
        
        # Month = Jan
        if month == 1:
            prescribed = 4.5
        # Month = Feb
        elif month == 2:
            prescribed = 8
        # Month = Mar - Apr
        elif month == 3 or month == 4:
            prescribed = 10
        # Month = May
        elif month == 5:
            prescribed = 8
        # Other
        else:
            prescribed = 4.5
        
        # Account for planning model
        if self.model.mode == "planning":
            prescribed *= self.days_in_month
        
        return prescribed
        
    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Browns_Creek_Ditch_Min_Flow.register()
