import pandas as pd
import numpy as np
import datetime as dt
from sierra.base_parameters import BaseParameter

from sierra.utilities.converter import convert


class Dion_R_Holm_PH_Demand(BaseParameter):
    """"""

    max_release_cms = 27.47

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        # Recreational flows - 9,000 AF/month, 4-5hrs/day except every other Weds.
        # Here, assume: 9,000 TAF * 5 months / ((153 total days - 11 Wednesdays) / 5 months) = 317 AF / day
        # 317 AF/day = 160 cfs = 4.52 cms
        recreation_cms = 0.0
        if 6 <= timestep.month <= 10:
            if timestep.dayofyear % 14:
                recreation_cms = 4.52

        elif timestep.index % 7:
            return self.model.nodes["Dion R Holm PH"].prev_flow[sid] / 0.0864

        # Cherry storage
        CH = self.model.nodes["Cherry Lake"]
        cherry_storage = CH.volume[sid]
        max_cherry_storage = CH.max_volume
        available_storage_mcm = max_cherry_storage - cherry_storage

        # get forecasted spill (assume perfect foresight)
        days = 60
        start = timestep.datetime
        end = start + dt.timedelta(days=days)
        forecast_dates = pd.date_range(start, end)

        EL_forecasted_inflow_mcm = self.model.parameters["Lake Eleanor Inflow/Runoff"].dataframe[forecast_dates].sum()
        CH_forecasted_inflow_mcm = self.model.parameters["Cherry Lake Inflow/Runoff"].dataframe[forecast_dates].sum()

        # forecasted_inflow_mcm = EL_forecasted_inflow_mcm + CH_forecasted_inflow_mcm
        forecasted_inflow_mcm = CH_forecasted_inflow_mcm

        forecasted_ifr_mcm = np.sum([15.5 if d.month in [7, 8, 9] else 6 for d in forecast_dates]) / 35.31 * 0.0864

        spill_release_cms = 0.0
        if forecasted_inflow_mcm - forecasted_ifr_mcm > available_storage_mcm:
            # spill_release_cms = (forecasted_inflow_mcm - available_storage_mcm) / days / 0.0864
            # spill_release_cms = (forecasted_inflow_mcm - available_storage_mcm) / 0.0864
            # spill_release_cms = min(spill_release_cms, self.max_release_cms)
            spill_release_cms = self.max_release_cms

        # Water Bank storage
        water_bank_storage = self.model.parameters["Water Bank"].get_value(scenario_index)
        water_bank_storage_curve = self.model.parameters["Water Bank Preferred Storage AF"] \
                                       .value(timestep, scenario_index) / 1000 * 1.2335

        water_bank_release_cms = 0.0
        # Cherry storage min threshold = 100 * 1.2335 = 123.5
        if cherry_storage >= 123.5 and water_bank_storage < water_bank_storage_curve:
            # release_cfs = 970 cfs = 27.47 cms
            # water_bank_release_cms = self.max_release_cms
            water_bank_release_cms = water_bank_storage_curve - water_bank_storage

        release_cms = max(spill_release_cms, water_bank_release_cms, recreation_cms)

        # release_cms *= 0.75

        return release_cms

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
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


Dion_R_Holm_PH_Demand.register()
