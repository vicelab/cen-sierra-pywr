from pywr.parameters import Parameter
import pandas as pd
import numpy as np
from datetime import datetime


class IFR_bl_Hetch_Hetchy_Reservoir_UTREP_Spill(Parameter):
    MIN_STORAGE_THRESHOLD_MCM = 100 * 1.2335  # Storage threshold below which snowmelt flows will not initiate
    STORAGE_FORECAST_THRESHOLD = 300 * 1.2335  # Storage forecast above which snowmelt releases should be initiated
    EXCESS_SPILL_THRESHOLD_AF = 10000  # Excess spill value above which the template hydrograph should be changed
    POWER_TUNNEL_MAX_MCM = 1250 / 35.315 * 0.0864
    LOW_SPILL_THRESHOLD_MCM = 30 * 1.2335

    # Though power tunnel max flow is dynamic, during UTREP releases it is assumed at capacity
    # If the actual capacity changes (not previously discussed as an option), then this can change as an input

    def setup(self, *args, **kwargs):
        super().setup()

        # Initial setup
        self.template_hydrographs_cfs = self.model.tables["IFR bl Hetch Hetchy Reservoir/UTREP hydrographs"]
        self.thresholds = [int(t) for t in self.template_hydrographs_cfs.columns]
        self.reversed_thresholds = list(reversed(self.thresholds))

        num_scenarios = len(self.model.scenarios.combinations)

        self.latest_start_date = [None] * num_scenarios
        self.fcst_spill_mcm = np.zeros(num_scenarios)
        self.spill_days = np.zeros(num_scenarios)
        self.excess_af = [None] * num_scenarios
        self.spill_threshold_af = np.empty(num_scenarios, dtype=int)
        self.base_template_hydrograph_cfs = [None] * num_scenarios
        self.adjusted_template_hydrograph_cfs = [None] * num_scenarios

    def get_forecasted_spill(self, timestep, scenario_index, current_storage, end_date=None, fcst_inflow=None,
                             days=None):
        # Estimate uncontrolled spill assuming snowmelt releases do not occur.

        hh_inflow_df = self.model.nodes['Hetch Hetchy Reservoir Inflow'].max_flow.dataframe

        # get end date if fcst_inflow is not supplied
        if fcst_inflow is None:
            if days and end_date is None:
                end_date = timestep.datetime + pd.DateOffset(days=days)

        total_spill = 0

        # Create dates for spill estimation period
        dates = pd.date_range(start=timestep.datetime, end=end_date, freq='D')
        storage = current_storage
        max_storage = self.model.nodes["Hetch Hetchy Reservoir"].max_volume
        wyt = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Water Year Type"].value(timestep, scenario_index)

        # Additional IFR (if power tunnel release >= 920 cfs)
        if wyt <= 2:
            # assume 64 cfs is required, since we're also assuming max power tunnel release
            add_ifr = 0.1565  # = 64 cfs in mcm
        else:
            add_ifr = 0

        # Evaporation assumption.
        # The spill routine already is slightly conservative, so zero can be assumed.
        evap = 0

        # get schedule
        schedule = self.model.tables["IFR bl Hetch Hetchy Reservoir/IFR Schedule"]

        # Calculate total spill as summation of daily spill

        # get lookup column
        lookup_col = min([3, 2, 1].index(wyt) * 2 + 1, 4)

        for date in dates:
            # get lookup row
            lookup_row = date.month - 1

            # factor of safety based on practice
            base_ifr_cfs = schedule.iat[lookup_row, lookup_col] + 5
            base_ifr = base_ifr_cfs / 35.31 * 0.0864  # convert to mcm

            inflow = hh_inflow_df[date]
            ifr = base_ifr + add_ifr  # units in mcm at this point
            available_storage = self.max_storage - storage
            daily_spill = max(inflow - available_storage - self.POWER_TUNNEL_MAX_MCM - evap - ifr, 0.0)
            storage = min(storage + inflow - self.POWER_TUNNEL_MAX_MCM - evap - ifr, max_storage)
            total_spill += daily_spill

        return total_spill

    def get_spill_threshold(self, value):
        # Get the spill threshold
        for threshold in self.reversed_thresholds:
            if value >= threshold:
                return threshold

        return 0

    def reset_state_variables(self, sid):
        self.latest_start_date[sid] = None
        self.fcst_spill_mcm[sid] = 0.0
        self.spill_days[sid] = 0.0
        self.excess_af[sid] = None
        self.spill_threshold_af[sid] = 0
        self.base_template_hydrograph_cfs[sid] = None
        self.adjusted_template_hydrograph_cfs[sid] = None

    def _value(self, timestep, scenario_index):

        sid = scenario_index.global_id

        # return 0.0
        if timestep.index == 0:
            # Work in AF for now
            self.max_storage = self.model.nodes['Hetch Hetchy Reservoir'].get_max_volume(scenario_index)

        if timestep.month == 10 and timestep.day == 1:
            self.reset_state_variables(sid)

        # Don't do any forecasting before April or after July, for efficiency and realistic operations
        if timestep.month < 4 or timestep.month > 7:
            return 0.0

        # General state variables
        current_storage_mcm = self.model.nodes['Hetch Hetchy Reservoir'].volume[scenario_index.global_id]

        # =========================
        # Spill forecasting routine
        # =========================

        # Compute forecast on first of month
        # Note: this assumes perfect foresight
        if timestep.month == 4 and timestep.day == 1:

            self.latest_start_date[sid] = datetime(timestep.year, 5, 15)

            forecast_end_date = datetime(timestep.year, 7, 15)

            self.fcst_spill_mcm[sid] \
                = self.get_forecasted_spill(timestep, scenario_index, current_storage_mcm, end_date=forecast_end_date)

            fcst_spill_af = self.fcst_spill_mcm[sid] / 1.2335 * 1e3

            spill_threshold_af = self.get_spill_threshold(fcst_spill_af)

            self.spill_threshold_af[sid] = spill_threshold_af
            if spill_threshold_af:
                self.base_template_hydrograph_cfs[sid] = self.template_hydrographs_cfs[str(spill_threshold_af)]

        fcst_spill_af = self.fcst_spill_mcm[sid] / 1.2335 * 1e3
        spill_threshold_af = self.spill_threshold_af[sid]

        if not fcst_spill_af or not spill_threshold_af:
            return 0.0

        # ======================
        # Get buffer coefficient
        # ======================
        release_coefficient = 1.0
        # current_storage_taf = current_storage_mcm / 1.2335
        # if current_storage_taf < 200:
        #     release_coefficient = 0.0
        # elif current_storage_taf < 210:
        #     release_coefficient = 0.25
        # elif current_storage_taf <= 225:
        #     release_coefficient = 0.5
        # elif current_storage_taf <= 250:
        #     release_coefficient = 0.75
        # else:
        #     release_coefficient = 1.0

        # ==================
        # UTREP spill lookup
        # ==================

        excess_af = self.excess_af[sid]
        if excess_af is None:
            excess_af = max(fcst_spill_af - spill_threshold_af, 0.0)
            self.excess_af[sid] = excess_af

            base_template_hydrograph_cfs = self.base_template_hydrograph_cfs[sid]
            self.adjusted_template_hydrograph_cfs[sid] = base_template_hydrograph_cfs

            if excess_af:
                if 66000 <= spill_threshold_af <= 178000 and spill_threshold_af != 104000:
                    # interpolate between this and next template hydrograph
                    next_threshold = self.thresholds[self.thresholds.index(spill_threshold_af) + 1]
                    next_hydrograph_cfs = self.template_hydrographs_cfs[str(next_threshold)]
                    alpha = excess_af / (next_threshold - spill_threshold_af)

                    adjusted_template_hydrograph_cfs = []
                    for i in range(len(base_template_hydrograph_cfs)):
                        adjusted_release_cfs = min(base_template_hydrograph_cfs[i] * (1 + alpha), next_hydrograph_cfs[i])
                        adjusted_template_hydrograph_cfs.append(adjusted_release_cfs)

                    self.adjusted_template_hydrograph_cfs[sid] = adjusted_template_hydrograph_cfs

        if not self.spill_days[sid]:

            # Check to see if we should start UTREP releases, based on:

            # ...storage threshold
            if current_storage_mcm <= self.MIN_STORAGE_THRESHOLD_MCM:
                return 0.0

            # ...storage forecast
            week_forecast = self.model.nodes['Hetch Hetchy Reservoir Inflow'].max_flow.dataframe[
                            timestep.datetime:timestep.datetime + pd.DateOffset(7)].sum()
            if current_storage_mcm + week_forecast - self.POWER_TUNNEL_MAX_MCM * 7 < self.STORAGE_FORECAST_THRESHOLD:
                return 0.0

        # initiate spill
        self.spill_days[sid] += 1

        if self.spill_days[sid] >= len(self.base_template_hydrograph_cfs[sid]):
            return 0.0
        release_cfs = self.adjusted_template_hydrograph_cfs[sid][self.spill_days[sid] - 1]

        # check if we have extra water to spill above threshold
        # there will probably always be extra
        if excess_af > self.EXCESS_SPILL_THRESHOLD_AF:
            # subtract amount from excess; convert to af
            excess_adjustment_af = release_cfs * 0.0864 / 43560.0 * release_coefficient
            if spill_threshold_af < 66000:
                # stay at the 700 cfs shelf level
                if release_cfs == 700:  # 1388 AF = 700 CFS
                    self.spill_days[sid] -= 1  # extend 700 CFS shelf
                    excess_af -= excess_adjustment_af

            elif spill_threshold_af == 104000:
                # stay at second 1300 cfs (2578 AF/d) shelf
                if self.spill_days[sid] == 22:
                    self.spill_days[sid] -= 1
                    excess_af -= excess_adjustment_af

            elif spill_threshold_af > 178000:
                # stay at this shelf level
                if self.spill_days[sid] > 2:
                    self.spill_days[sid] -= 1
                    excess_af -= excess_adjustment_af  # subtract release at this shelf level from excess

            self.excess_af[sid] = excess_af

        # account for base IFR already being released
        ifr_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Base Flow"].get_value(scenario_index)

        utrep_mcm = release_cfs / 35.315 * 0.0864
        # release_mcm = max(utrep_mcm - ifr_mcm, 0.0) * release_coefficient
        release_mcm = utrep_mcm * release_coefficient

        return release_mcm

    def value(self, *args, **kwargs):
        try:
            return self._value(*args, **kwargs)
        except Exception as err:
            print('ERROR for parameter {}'.format(self.name))
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Hetch_Hetchy_Reservoir_UTREP_Spill.register()
