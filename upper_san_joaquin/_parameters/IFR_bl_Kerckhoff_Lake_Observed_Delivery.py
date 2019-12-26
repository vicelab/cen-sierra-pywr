from parameters import WaterLPParameter

from utilities.converter import convert

class IFR_bl_Kerckhoff_Lake_Observed_Delivery(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # this could also be moved to an flow gauge node
        #path="{LocalDir}/GAGES/Streamflow/USGS_11246700.csv".format(LocalDir=self.get("RCP", **kwargs))
        #week = periodic_timestep + 39 if date.month >= 10 else periodic_timestep - 13 # TODO: make this kind of variable availabe to all functions?
        #data = self.read_csv(path, index_col=[0,1], squeeze=True, parse_dates=False, header=None, comment=';', **kwargs)
        #return data[date.year, week] if (date.year, week) in data else 0
        return 0
        
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
        
IFR_bl_Kerckhoff_Lake_Observed_Delivery.register()
print(" [*] IFR_bl_Kerckhoff_Lake_Observed_Delivery successfully registered")
