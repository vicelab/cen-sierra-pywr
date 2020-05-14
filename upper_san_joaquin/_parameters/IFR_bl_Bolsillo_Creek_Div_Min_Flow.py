from parameters import MinFlowParameter

from utilities.converter import convert

class IFR_bl_Bolsillo_Creek_Div_Min_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):
        
        ifr_cfs = 0.4
        
        if self.model.mode == "planning":
            ifr_cfs *= self.days_in_month
        
        return ifr_cfs / 35.31
        
    def value(self, *args, **kwargs):
        try:
            ifr = self.get_ifr(*args, **kwargs)
            if ifr is not None:
                return ifr
            else:
                ifr = self._value(*args, **kwargs)
                return ifr # unit is already mcm
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            
    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise
        
IFR_bl_Bolsillo_Creek_Div_Min_Flow.register()
