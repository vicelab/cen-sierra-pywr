import pandas as pd
from datetime import timedelta
from sierra.base_parameters import BaseParameter


class Lake_Eleanor_Forecasted_Inflow(BaseParameter):

    def _value(self, timestep, scenario_index):

        # get forecasted spill (60 days out; assume perfect foresight)
        start = timestep.datetime
        end = start + timedelta(days=60)
        forecast_dates = pd.date_range(start, end)
        forecasted_inflow_mcm = self.model.parameters["Lake Eleanor Inflow/Runoff"].dataframe[forecast_dates].sum()

        # get forecasted IFR
        forecasted_ifr_mcm = 0
        for date in forecast_dates:
            md = (date.month, date.day)
            if (4, 1) <= md <= (5, 14) or (9, 16) <= md <= (10, 31):
                ifr_cfs = 10
            elif (5, 15) <= md <= (9, 15):
                ifr_cfs = 20
            else:
                ifr_cfs = 5
            forecasted_ifr_mcm += ifr_cfs / 35.315 * 0.0864

        forecasted_inflow_mcm -= forecasted_ifr_mcm

        return forecasted_inflow_mcm

    def value(self, timestep, scenario_index):
        try:
            return self._value(timestep, scenario_index)
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


Lake_Eleanor_Forecasted_Inflow.register()
