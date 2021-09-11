from sierra.base_parameters import BaseParameter


class Eleanor_Cherry_Pumping_Requirement(BaseParameter):

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        EL = self.model.nodes["Lake Eleanor"]

        EL_storage_mcm = EL.volume[sid]

        prev_pumping = self.model.nodes["Eleanor-Cherry Pumping"].prev_flow[sid]

        can_release = EL_storage_mcm >= 20.36 or prev_pumping and timestep.index % 7

        if not can_release:
            return 0.0

        # If we start pumping, keep pumping for 1 week
        if prev_pumping and timestep.index % 7:
            return prev_pumping

        # If Eleanor will likely spill and current storage is above the target storage, then pump

        # get forecasted spill (60 days out; assume perfect foresight)
        forecasted_inflow_mcm = self.model.parameters["Lake Eleanor/Forecasted Inflow"].get_value(scenario_index)

        # get available storage
        available_storage = EL.max_volume - EL_storage_mcm

        pumping_flow_mcm = 0.0

        if forecasted_inflow_mcm >= available_storage:

            # Get storage target
            # storage_target_mcm \
            #     = self.model.tables["Lake Eleanor Pumping Thresholds"][timestep.datetime.dayofyear] / 1000 * 1.2335

            CH = self.model.nodes["Cherry Lake"]

            CH_elev = CH.get_level(scenario_index)
            EL_elev = EL.get_level(scenario_index)
            EL_CH_head_m = EL_elev - CH_elev
            EL_CH_head_ft = EL_CH_head_m / 3.048

            # Gravity flow (Eleanor is higher than Cherry)
            if EL_CH_head_m <= 0:
                # pumping_AF = min(max(-0.034 * -EL_CH_head_ft ** 2 - 5.3068 * -EL_CH_head_ft + 595.72, 0), 1200)
                pumping_cfs = min(max(-0.0171 * -EL_CH_head_ft ** 2 - 0.077 * -EL_CH_head_ft + 300.34, 0), 605)
                pumping_flow_mcm = pumping_cfs / 35.315 * 0.0864

        return pumping_flow_mcm

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


Eleanor_Cherry_Pumping_Requirement.register()
