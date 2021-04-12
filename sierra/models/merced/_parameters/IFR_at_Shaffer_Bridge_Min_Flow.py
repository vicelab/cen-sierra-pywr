from datetime import date
import numpy as np
from sierra.base_parameters import MinFlowParameter
from sierra.utilities.converter import convert


class IFR_at_Shaffer_Bridge_Min_Flow(MinFlowParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    # initialize some values
    ferc_wyt = 1
    cowell_day_cnt = 0
    nov_dec_mean = 0
    ifr_names = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()
        self.nov_dec_mean = np.zeros(self.num_scenarios)
        self.cowell_day_cnt = np.zeros(self.num_scenarios)

    def _value(self, timestep, scenario_index):
        # All flow units are in cubic meters per second (cms) unless otherwise noted

        if timestep.month == 10 and timestep.day <= 10 and timestep.index:
            ifr_mcm = self.model.nodes["IFR at Shaffer Bridge"].prev_flow[scenario_index.global_id]
            return ifr_mcm / 0.0864  # convert to cms

        # FERC REQUIREMENT
        WYT = self.model.tables['WYT for IFR Below Exchequer'][self.operational_water_year]
        ferc_flow_req = self.ferc_req(timestep, scenario_index, WYT)

        # DAVIS-GRUNSKY AGREEMENT REQUIREMENT
        dga_flow_req = self.dga_requirement(timestep)

        # COWELL AGREEMENT REQUIREMENT
        ca_flow_req = self.ca_requirement(timestep, scenario_index)

        # FISH PULSE REQUIREMENT
        # TODO: revise table to lookup by month, day rather than 1900 year (this method is slow)
        fish_pulse = self.model.tables["Fish Pulse"]['1900-{:02}-{:02}'.format(timestep.month, timestep.day)] / 35.315

        # The required flow is (greater of the Davis-Grunsky and FERC flows)
        # + the Cowell Agreement entitlement + Fish Pulse + Diversion Reg
        requirement_cms = max(ferc_flow_req, dga_flow_req) + ca_flow_req + fish_pulse

        # previous_flow_mcm = self.model.nodes['IFR at Shaffer Bridge'].prev_flow[scenario_index.global_id]
        # downramp_mcm = self.get_down_ramp_ifr(timestep, scenario_index, previous_flow_mcm, rate=0.25)
        # requirement_mcm = max(requirement_mcm, swrcb_reqt_mcm)
        return requirement_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    def ferc_req(self, timestep, scenario_index, wyt):
        #sid = scenario_index.global_id
        month = timestep.month
        day = timestep.day
        year = timestep.year
        # FERC License: Different flows for wet and dry year
        # If the average streamflow maintained at Shaffer Bridge
        # from November 1 through December 31 is greater than 150 cubic feet per second (4.25 cms) exclusive of
        # flood spills and emergency releases, then the streamflows from January 1 through March 31
        # shall be maintained at 100 cubic feet per second (2.83 cms) or more.

        if wyt == 1:  # Wet Year
            if month == 10:
                if day < 15:
                    ferc_lic_flow = 0.71  # 25 cfs
                else:
                    ferc_lic_flow = 2.12  # 75 cfs
            elif month in (11, 12):
                ferc_lic_flow = 2.83  # 100 cfs
            elif month in (1, 2, 3, 4, 5):
                ferc_lic_flow = 2.12  # 75 cfs
            else:
                ferc_lic_flow = 0.71  # 25 cfs
        else:  # Dry Year
            if month == 10:
                if day < 15:
                    ferc_lic_flow = 0.43  # 15 cfs
                else:
                    ferc_lic_flow = 1.7  # 60 cfs
            elif month in (11, 12):
                ferc_lic_flow = 2.12  # 75 cfs
            elif month in (1, 2, 3, 4, 5):
                ferc_lic_flow = 1.7  # 60 cfs
            else:
                ferc_lic_flow = 0.43  # 15 cfs

        if (month, day) == (1, 1):
            # Calculate for average flow in Nov and Dec of previous year at Shaffer Bridge on 1st Jan
            st_date = date(year - 1, 11, 1)
            end_date = date(year - 1, 12, 31)
            gauge_Shafer_ts = self.model.recorders['IFR at Shaffer Bridge/flow'].to_dataframe()

            # TODO: find a more efficient lookup method than iloc
            self.nov_dec_mean[scenario_index.global_id] = gauge_Shafer_ts[st_date:end_date].mean().values[0]

        if month in (1, 2, 3):
            # If mean flow greater than eaual to 150 cfs, then at least 100 cfs flow
            if self.nov_dec_mean[scenario_index.global_id] >= 4.25:
                ferc_lic_flow = 2.83

        return ferc_lic_flow

    def dga_requirement(self, timestep):
        # Davis-Grunsky Agreement
        # Flow required from Nov to March - 180 to 220 cfs. Using average value of 200 cfs(5.66 cms)
        if timestep.year <= 2017:  # The agreement expired in 2017
            if timestep.month in (11, 12, 1, 2, 3):
                davis_grunsky_flow = 5.66
            else:
                davis_grunsky_flow = 0
        else:
            davis_grunsky_flow = 0

        return davis_grunsky_flow

    def ca_requirement(self, timestep, scenario_index):
        # Cowell Agreement
        month = timestep.month
        day = timestep.day

        # reset day count
        if (month, day) == (10, 1):
            self.cowell_day_cnt[scenario_index.global_id] = 0

        cowell_flow = 0

        # don't load inflow_NED_ts unless needed
        if month == 3:
            # Flow of 100 cfs (2.832 cms)
            cowell_flow = 2.832
        elif month == 4:
            # Flow of 175 cfs (4.955 cms)
            cowell_flow = 4.955
        elif month == 5:
            # Flow of 225 cfs (6.371 cms)
            cowell_flow = 6.371

        else:

            # Calculate the natural flow
            # Because this should depend on the current timestep's inflow, inflow data should be
            # loaded all at once, then replace prev_flow with flow
            flow_val = self.model.parameters["Full Natural Flow"].value(timestep, scenario_index) / 0.0864  # mcm to cms

            if month in (10, 11, 12, 1, 2):
                # Flow of 50 cfs (1.416 cms) only from Exchequer flows
                # if flow_val >= 1.416:
                cowell_flow = 1.416
                # else:
                #     cowell_flow = 0
            elif month in (6, 7, 8, 9):
                # Sustain 250 cfs (7.08 cms) until inflow to NE falls below 1,200 cfs (33.98 cms),
                # then 225 cfs (6.37 cms) for 31 days,175 cfs (4.96 cms) for 31 days, and 150 cfs (4.25 cms) for 30 days
                # Loop through ExChequer inflow data

                day_cnt = self.cowell_day_cnt[scenario_index.global_id]

                if day_cnt:
                    day_cnt += 1
                elif flow_val < 33.98:
                    day_cnt = 1

                if day_cnt == 0:  # Flow never went below 1200 cfs
                    cowell_flow = 7.08  # Sustain 250 cfs
                elif day_cnt <= 31:
                    cowell_flow = 6.37
                elif day_cnt <= 62:
                    cowell_flow = 4.96
                else:
                    cowell_flow = 4.25

                # update state
                self.cowell_day_cnt[scenario_index.global_id] = day_cnt

        return cowell_flow

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_at_Shaffer_Bridge_Min_Flow.register()
