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

        EL_storage = EL.volume[scenario_index.global_id]

        # Turn pumping on if reservoir is full
        if EL_storage >= EL.max_volume * 0.95:
            self.can_pump[sid] = True

        EL_CH_transfer_mcm = 0.0

        if not self.can_pump[sid]:
            self.prev_pumping[sid] = 0.0
            return 0.0

        # If we start pumping, keep pumping for 1 week
        if timestep.index % 7 != 0 and self.prev_pumping[sid]:
            return self.prev_pumping[sid]

        self.prev_pumping[sid] = 0.0

        available_storage = EL.max_volume - EL_storage

        start = timestep.datetime
        end = start + timedelta(days=60)
        forecast = self.model.parameters["Lake Eleanor Inflow/Runoff"].dataframe[start:end].sum()

        # Reading the preferred storage for the current time step
        storage_target_mcm \
            = self.model.tables["Lake Eleanor Pumping Thresholds"][timestep.datetime.dayofyear] / 1000 * 1.2335

        # If Eleanor will likely spill and current storage is above the target storage, then pump
        if forecast >= available_storage and EL_storage >= storage_target_mcm:

            CH_elev = self.model.nodes["Cherry Lake"].get_level(scenario_index)
            EL_elev = self.model.nodes["Lake Eleanor"].get_level(scenario_index)
            EL_CH_head_m = EL_elev - CH_elev
            EL_CH_head_ft = EL_CH_head_m / 3.048

            gravity_flow_mcm = 0.0
            pumping_flow_mcm = 0.0
            max_release = 2.447  # TODO: double check this number

            # Gravity flow (Eleanor is higher than Cherry)
            if EL_CH_head_m > 0:
                month = timestep.month
                summer = [7, 8, 9]
                min_EL_summer_storage = 17900 / 1e3 * 1.2335
                min_EL_nonsummer_storage = 5000 / 1e3 * 1.2335
                if month in summer and EL_storage >= min_EL_summer_storage \
                        or month not in summer and EL_storage >= min_EL_nonsummer_storage:
                    gravity_AF = min(211.88 * EL_CH_head_ft ** 0.5255, 1980)
                    gravity_flow_mcm = gravity_AF / 1e3 * 1.2335
                    self.prev_pumping[sid] = 0.0

            # Pumping flow (Cherry is higher than Eleanor)
            if EL_CH_head_m <= 0:
                pumping_AF = min(max(-0.034 * (-EL_CH_head_ft) ** 2 - 5.3068 * (-EL_CH_head_ft) + 595.72, 0), 1200)
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
