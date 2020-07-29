import pandas as pd
import numpy as np
from datetime import timedelta
from parameters import WaterLPParameter


class Eleanor_Cherry_Pumping_Station_Requirement(WaterLPParameter):
    can_pump = None
    prev_pumping = None

    def setup(self):
        super().setup()
        num_scenarios = len(self.model.scenarios.combinations)
        self.can_pump = np.zeros(num_scenarios, np.bool)
        self.prev_pumping = np.zeros(num_scenarios, np.bool)

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        EL = self.model.nodes["Lake Eleanor"]

        # Turn pumping off Jan 1
        if timestep.datetime.dayofyear == 1:
            self.can_pump[sid] = False

        EL_storage_mcm = EL.volume[sid]
        prev_pumping = self.prev_pumping[sid]

        self.can_pump[sid] = EL_storage_mcm >= 20.36 or prev_pumping and timestep.index % 7

        # If we start pumping, keep pumping for 1 week
        if timestep.index % 7 and prev_pumping:
            return prev_pumping

        self.prev_pumping[sid] = 0.0

        # Initial transfer (none)
        EL_CH_transfer_mcm = 0.0

        # If Eleanor will likely spill and current storage is above the target storage, then pump

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
        
        # get available storage
        available_storage = EL.max_volume - EL_storage_mcm

        if forecasted_inflow_mcm >= available_storage:

            # Get storage target
            # storage_target_mcm \
            #     = self.model.tables["Lake Eleanor Pumping Thresholds"][timestep.datetime.dayofyear] / 1000 * 1.2335

            CH = self.model.nodes["Cherry Lake"]

            CH_elev = CH.get_level(scenario_index)
            EL_elev = EL.get_level(scenario_index)
            EL_CH_head_m = EL_elev - CH_elev
            EL_CH_head_ft = EL_CH_head_m / 3.048

            gravity_flow_mcm = 0.0
            pumping_flow_mcm = 0.0

            # Gravity flow (Eleanor is higher than Cherry)
            if EL_CH_head_m > 0:
                month = timestep.month
                summer = [7, 8, 9]
                min_EL_summer_storage = 17900 / 1e3 * 1.2335
                min_EL_nonsummer_storage = 5000 / 1e3 * 1.2335
                if month in summer and EL_storage_mcm >= min_EL_summer_storage \
                        or month not in summer and EL_storage_mcm >= min_EL_nonsummer_storage:
                    gravity_AF = min(211.88 * EL_CH_head_ft ** 0.5255, 1980)
                    gravity_flow_mcm = gravity_AF / 1e3 * 1.2335
                    self.prev_pumping[sid] = 0.0

            # Pumping flow (Cherry is higher than Eleanor)
            else:
                pumping_AF = min(max(-0.034 * -EL_CH_head_ft ** 2 - 5.3068 * -EL_CH_head_ft + 595.72, 0), 1200)
                pumping_flow_mcm = pumping_AF / 1e3 * 1.2335
                self.prev_pumping[sid] = pumping_flow_mcm

            EL_CH_transfer_mcm = gravity_flow_mcm + pumping_flow_mcm

        return EL_CH_transfer_mcm

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


Eleanor_Cherry_Pumping_Station_Requirement.register()
