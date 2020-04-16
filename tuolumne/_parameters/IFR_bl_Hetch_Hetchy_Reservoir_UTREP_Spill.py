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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_state_variables()

    def setup(self, *args, **kwargs):
        super().setup()

        # Initial setup
        self.template_hydrographs = self.model.tables["IFR bl Hetch Hetchy Reservoir/UTREP hydrographs"]
        self.thresholds = [int(t) for t in self.template_hydrographs.columns]
        self.reversed_thresholds = list(reversed(self.thresholds))

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

    # def get_forecasted_storage(self, timestep, scenario_index, current_storage, days):
    #     # Get approximate storage
    #     # Note that the assumption of full power tunnel release will result in more conservative operations
    #
    #     hh_inflow_df = self.model.nodes['Hetch Hetchy Reservoir Inflow'].max_flow.dataframe
    #     fcst_inflow = hh_inflow_df[timestep.datetime:timestep.datetime + pd.DateOffset(days)].sum()
    #     forecasted_spill = \
    #         self.get_forecasted_spill(timestep, scenario_index, current_storage, fcst_inflow=fcst_inflow, days=days)
    #     forecasted_storage = current_storage + fcst_inflow - self.POWER_TUNNEL_MAX_MCM * days - forecasted_spill
    #
    #     return forecasted_storage

    def get_spill_threshold(self, value):
        # Get the spill threshold
        for threshold in self.reversed_thresholds:
            if value >= threshold:
                return threshold

    def reset_state_variables(self):
        self.start_date = None
        self.latest_start_date = None
        self.should_spill = False
        self.fcst_spill_mcm = 0
        self.spill_days = 0
        self.excess_af = None
        self.days_at_threshold = 0
        self.released_to_date = 0
        self.flow_volume_index = 0
        self.down_ramp = 1.0
        self.low_spill_year = False
        self.centroid_date = None
        self.spill_threshold_af = 0

    def value(self, timestep, scenario_index):
        # return 0.0
        if timestep.index == 0:
            # Work in AF for now
            self.max_storage = self.model.nodes['Hetch Hetchy Reservoir'].get_max_volume(scenario_index)

        if timestep.month == 10:
            self.reset_state_variables()

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

            self.latest_start_date = datetime(timestep.year, 5, 15)

            forecast_end_date = datetime(timestep.year, 7, 15)

            self.fcst_spill_mcm \
                = self.get_forecasted_spill(timestep, scenario_index, current_storage_mcm, end_date=forecast_end_date)
            self.low_spill_year = self.fcst_spill_mcm <= self.LOW_SPILL_THRESHOLD_MCM

            fcst_spill_af = self.fcst_spill_mcm / 1.2335 * 1e3
            self.spill_threshold_af = self.get_spill_threshold(fcst_spill_af)
            if self.spill_threshold_af:
                self.template_hydrograph_af = self.template_hydrographs[str(self.spill_threshold_af)]

        if not self.fcst_spill_mcm or not self.spill_threshold_af:
            return 0.0

        # ======================
        # Get buffer coefficient
        # ======================
        release_coefficient = 1.0
        current_storage_taf = current_storage_mcm / 1.2335
        if current_storage_taf < 200:
            release_coefficient = 0.0
        elif current_storage_taf < 210:
            release_coefficient = 0.25
        elif current_storage_taf <= 225:
            release_coefficient = 0.5
        elif current_storage_taf <= 250:
            release_coefficient = 0.75
        else:
            release_coefficient = 1.0

        # ==================
        # UTREP spill lookup
        # ==================

        if self.excess_af is None:
            fcst_spill_af = self.fcst_spill_mcm / 1.2335 * 1e3
            self.excess_af = max(fcst_spill_af - self.spill_threshold_af, 0.0)

            if self.excess_af:
                if 66000 <= self.spill_threshold_af <= 178000 and self.spill_threshold_af != 104000:
                    # interpolate between this and next template hydrograph
                    next_threshold = self.thresholds[self.thresholds.index(self.spill_threshold_af) + 1]
                    next_hydrograph = self.template_hydrographs[str(next_threshold)]
                    alpha = self.excess_af / (next_threshold - self.spill_threshold_af)

                    self.template_hydrograph_af = [min(self.template_hydrograph_af[i] * (1 + alpha), next_hydrograph[i])
                                                for i in range(len(self.template_hydrograph_af))]

        if not self.spill_days:

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
        self.spill_days += 1

        if self.spill_days >= len(self.template_hydrograph_af):
            return 0.0
        release_af = self.template_hydrograph_af[self.spill_days - 1]

        # check if we have extra water to spill above threshold
        # there will probably always be extra
        if self.excess_af > self.EXCESS_SPILL_THRESHOLD_AF:

            if self.spill_threshold_af < 66000:
                # stay at the 700 cfs shelf level
                if release_af == 1388.0:  # 1388 AF = 700 CFS
                    self.spill_days -= 1  # extend 700 CFS shelf
                    self.excess_af -= release_af * release_coefficient  # subtract amount from excess

            elif self.spill_threshold_af == 104000:
                # stay at second 1300 cfs (2578 AF/d) shelf
                if self.spill_days == 22:
                    self.spill_days -= 1
                    self.excess_af -= release_af * release_coefficient

            elif self.spill_threshold_af > 178000:
                # stay at this shelf level
                if self.spill_days > 2:
                    self.spill_days -= 1
                    self.excess_af -= release_af * release_coefficient  # subtract release at this shelf level from excess

        # account for base IFR already being released
        ifr_mcm = self.model.parameters["IFR bl Hetch Hetchy Reservoir/Base Flow"].value(timestep, scenario_index)

        utrep_mcm = release_af / 1e3 * 1.2335
        release_mcm = max(utrep_mcm - ifr_mcm, 0.0) * release_coefficient

        # self.released_to_date += release_mcm

        return release_mcm

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Hetch_Hetchy_Reservoir_UTREP_Spill.register()
