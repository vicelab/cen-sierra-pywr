from parameters import WaterLPParameter
from datetime import date
import numpy as np


class IFR_at_Shaffer_Bridge_Min_Flow(WaterLPParameter):
    """
    This policy calculates instream flow requirements in the Merced River below the Merced Falls powerhouse.
    """

    # initialize some values
    ferc_wyt = 1
    cowell_day_cnt = 0
    nov_dec_mean = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load the water year types
        # TODO: this should be moved to real-time lookup to be scenario-dependent
        # We should be able to add a "WYT" parameter as a general variable and save it to parameters in the JSON file.
        # It could be pre-processed, as currently, or calculated on-the-fly
        csv_kwargs = dict(index_col=0, header=0, parse_dates=False, squeeze=True)
        self.fish_data = self.read_csv('Management/BAU/Demand/fishPulse_Merced_cfs.csv',
                                       **csv_kwargs) / 35.3147  # Converting to cms
        self.div_data = self.read_csv('Management/BAU/Demand/otherDiversions_Merced_cfs.csv',
                                      **csv_kwargs) / 35.3147  # Converting to cms

        swrcb_levels_count = self.model.scenarios['SWRCB 40'].size
        if swrcb_levels_count == 1:
            self.swrcb_levels = [0.0] # baseline scenario only
        else:
            self.swrcb_levels = np.arange(0.0, 0.41, 0.4 / (swrcb_levels_count - 1))

    def value(self, timestep, scenario_index):
        # All flow units are in cubic meters per second (cms)

        # FERC REQUIREMENT
        wyt = self.model.tables['WYT for IFR Below Exchequer'][timestep.year]
        ferc_flow_req = self.ferc_req(timestep, scenario_index, wyt)

        # DAVIS-GRUNSKY AGREEMENT REQUIREMENT
        dga_flow_req = self.dga_requirement(timestep)

        # COWELL AGREEMENT REQUIREMENT
        ca_flow_req = self.ca_requirement(timestep)

        # FISH PULSE REQUIREMENT
        fish_req = self.fish_requirement(timestep)

        # DIVERSION REQUIREMENT
        dev_req = self.dev_requirement(timestep)

        # SCWRB 40 REQUIREMENT
        swrcb_reqt_mcm = 0.0
        if 2 <= timestep.month <= 7:
            swrcb_reqt_mcm = self.swrcb_40_requirement(timestep, scenario_index)

        # The required flow is (greater of the Davis-Grunsky and FERC flows) + the Cowell Agreement entitlement + Fish Pulse + Diversion Reg
        requirement_cms = max(ferc_flow_req, dga_flow_req) + ca_flow_req + fish_req + dev_req
        requirement_mcm = requirement_cms * 0.0864  # convert to mcm

        requirement_mcm = max(requirement_mcm, swrcb_reqt_mcm)

        final_reqt_cms = self.get_down_ramp_ifr(timestep, scenario_index, requirement_mcm, rate=0.25)

        return final_reqt_cms * 0.0864

    def ferc_req(self, timestep, scenario_index, wyt):
        mth = timestep.month
        dy = timestep.day
        yr = timestep.year
        # FERC License: Different flows for wet and dry year
        # If the average streamflow maintained at Shaffer Bridge
        # from November 1 through December 31 is greater than 150 cubic feet per second (4.25 cms) exclusive of
        # flood spills and emergency releases, then the streamflows from January 1 through March 31
        # shall be maintained at 100 cubic feet per second (2.83 cms) or more.

        if wyt == 1:  # Wet Year
            if mth == 10:
                if dy < 15:
                    ferc_lic_flow = 0.71  # 25 cfs
                else:
                    ferc_lic_flow = 2.12  # 75 cfs
            elif mth in (11, 12):
                ferc_lic_flow = 2.83  # 100 cfs
            elif mth in (1, 2, 3, 4, 5):
                ferc_lic_flow = 2.12  # 75 cfs
            else:
                ferc_lic_flow = 0.71  # 25 cfs
        else:  # Dry Year
            if mth == 10:
                if dy < 15:
                    ferc_lic_flow = 0.43  # 15 cfs
                else:
                    ferc_lic_flow = 1.7  # 60 cfs
            elif mth in (11, 12):
                ferc_lic_flow = 2.12  # 75 cfs
            elif mth in (1, 2, 3, 4, 5):
                ferc_lic_flow = 1.7  # 60 cfs
            else:
                ferc_lic_flow = 0.43  # 15 cfs

        if mth in (1, 2, 3):
            if mth == 1 and dy == 1:
                # Calculate for average flow in Nov and Dec of previous year at Shaffer Bridge on 1st Jan
                st_date = date(yr - 1, 11, 1)
                end_date = date(yr - 1, 12, 31)
                gauge_Shafer_ts = self.model.recorders['IFR at Shaffer Bridge/flow'].to_dataframe()
                self.nov_dec_mean = gauge_Shafer_ts[tuple(scenario_index.indices)][st_date:end_date].mean()
            if self.nov_dec_mean >= 4.25:  # If mean flow greater than eaual to 150 cfs, then atleast 100 cfs flow
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

    def ca_requirement(self, timestep):
        # Cowell Agreement
        mth = timestep.month

        # reset day count
        if mth == 10:
            self.cowell_day_cnt = 0

        cowell_flow = 0

        # don't load inflow_NED_ts unless needed
        if mth == 3:
            # Flow of 100 cfs (2.832 cms)
            cowell_flow = 2.832
        elif mth == 4:
            # Flow of 175 cfs (4.955 cms)
            cowell_flow = 4.955
        elif mth == 5:
            # Flow of 225 cfs (6.371 cms)
            cowell_flow = 6.371

        else:

            # Calculate the natural flow
            # Because this should depend on the current timestep's inflow, inflow data should be
            # loaded all at once, then replace prev_flow with flow                                                                                             scenario_index)

            flow_val = self.model.tables["Full Natural Flow"][timestep.datetime] / 0.0864 # mcm to cms

            if mth in (10, 11, 12, 1, 2):
                # Flow of 50 cfs (1.416 cms) -only from ExChequer flows
                if flow_val >= 1.416:
                    cowell_flow = 1.416
                else:
                    cowell_flow = 0
            elif mth in (6, 7, 8, 9):
                # Sustain 250 cfs (7.08 cms) until inflow to NE falls below 1,200 cfs (33.98 cms),
                # then 225 cfs (6.37 cms) for 31 days,175 cfs (4.96 cms) for 31 days, and 150 cfs (4.25 cms) for 30 days
                # Loop through ExChequer inflow data

                dy_cnt = self.cowell_day_cnt

                if dy_cnt:
                    dy_cnt += 1
                elif flow_val < 33.98:
                    dy_cnt = 1

                if dy_cnt == 0:  # Flow never went below 1200 cfs
                    cowell_flow = 7.08  # Sustain 250 cfs
                elif dy_cnt <= 31:
                    cowell_flow = 6.37
                elif dy_cnt <= 62:
                    cowell_flow = 4.96
                else:
                    cowell_flow = 4.25

                # update state
                self.cowell_day_cnt = dy_cnt

        return cowell_flow

    def fish_requirement(self, timestep):
        return self.fish_data['1900-{:02}-{:02}'.format(timestep.month, timestep.day)]

    def dev_requirement(self, timestep):
        return self.div_data['1900-{:02}-{:02}'.format(timestep.month, timestep.day)]

    def swrcb_40_requirement(self, timestep, scenario_index):
        fnf = self.model.tables['Full Natural Flow'][timestep.datetime]
        return fnf * self.swrcb_levels[scenario_index.indices[0]]

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_at_Shaffer_Bridge_Min_Flow.register()
print(" [*] IFR_at_Shaffer_Bridge_Min_Flow successfully registered")
