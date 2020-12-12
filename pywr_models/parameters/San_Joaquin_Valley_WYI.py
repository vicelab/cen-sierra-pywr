from pywr_models.base_parameters import WaterLPParameter


class San_Joaquin_Valley_WYI(WaterLPParameter):
    """
    San Joaquin Valley Water Year Index = 0.6 * Current Apr-Jul Runoff Forecast (in maf)
   + 0.2 * Current Oct-Mar Runoff in (maf) + 0.2 * Previous Water Year's Index
   (if the Previous Water Year's Index exceeds 4.5, then 4.5 is used).
   This index, originally specified in the 1995 SWRCB Water Quality Control Plan,
   is used to determine the San Joaquin Valley water year type as implemented in
   SWRCB D-1641.  Year types are set by first of month forecasts beginning in
   February.  Final determination for San Joaquin River flow objectives is based
   on the May 1 75% exceedence forecast.
    """

    def _value(self, timestep, scenario_index):
        sjvi = self.model.tables["San Joaquin Valley Index"]
        if 4 <= self.datetime.month <= 12:
            operational_water_year = self.datetime.year
        else:
            operational_water_year = self.datetime.year - 1
        return sjvi[operational_water_year]

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
        except Exception as err:
            print('\nERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


San_Joaquin_Valley_WYI.register()
