from sierra.base_parameters import BaseParameter


class Eleanor_Cherry_Gravity_Requirement(BaseParameter):

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        EL = self.model.nodes["Lake Eleanor"]

        EL_storage_mcm = EL.volume[sid]

        prev_pumping = self.model.nodes["Eleanor-Cherry Pumping"].prev_flow[sid]
        prev_gravity = self.model.nodes["Eleanor-Cherry Gravity"].prev_flow[sid]

        # can_release = EL_storage_mcm >= 20.36 or prev_gravity_flow and timestep.index % 7
        can_release = EL_storage_mcm >= 0 or prev_gravity and not prev_pumping and timestep.index % 7

        if not can_release:
            return 0.0

        # If Eleanor will likely spill and current storage is above the target storage, then release

        # get forecasted spill (60 days out; assume perfect foresight)
        forecasted_inflow_mcm = self.model.parameters["Lake Eleanor/Forecasted Inflow"].get_value(scenario_index)

        # get available storage
        available_storage = EL.max_volume - EL_storage_mcm

        gravity_flow_mcm = 0.0

        if True or prev_gravity and timestep.index % 7:
        # if forecasted_inflow_mcm >= available_storage or prev_gravity and timestep.index % 7:

            # Get storage target
            # storage_target_mcm \
            #     = self.model.tables["Lake Eleanor Pumping Thresholds"][timestep.datetime.dayofyear] / 1000 * 1.2335

            CH = self.model.nodes["Cherry Lake"]

            CH_elev = CH.get_level(scenario_index)
            EL_elev = EL.get_level(scenario_index)
            EL_CH_head_m = EL_elev - CH_elev
            EL_CH_head_ft = EL_CH_head_m / 3.048

            # Gravity flow (Eleanor is higher than Cherry)
            if EL_CH_head_m > 0:
                month = timestep.month
                summer = [7, 8, 9]
                # min_EL_summer_storage = 17900 / 1e3 * 1.2335
                min_EL_summer_storage = 17900 / 1e3 * 1.2335
                min_EL_nonsummer_storage = 5000 / 1e3 * 1.2335
                if month in summer and EL_storage_mcm >= min_EL_summer_storage \
                        or month not in summer and EL_storage_mcm >= min_EL_nonsummer_storage:
                    # gravity_AF = min(211.88 * EL_CH_head_ft ** 0.5255, 1980)
                    gravity_cfs = min(106.8 * EL_CH_head_ft ** 0.5255, 998.25)
                    gravity_flow_mcm = gravity_cfs / 35.315 * 0.0864

        return gravity_flow_mcm

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


Eleanor_Cherry_Gravity_Requirement.register()
