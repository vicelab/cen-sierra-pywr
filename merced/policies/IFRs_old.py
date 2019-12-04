from parameters import WaterLPParameter
from datetime import date


class Requirement_Merced_R_below_Merced_Falls_PH(WaterLPParameter):
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
        self.wyts = self.read_csv('Scenarios/Livneh/preprocessed/WYT.csv', index_col=0, header=None, parse_dates=False,
                                  squeeze=True)

    def value(self, timestep, scenario_index):
        # All flow units are in cubic meters per second (cms)

        # FERC REQUIREMENT
        if (timestep.month, timestep.day) in [(10, 1), (1, 1)]:
            self.wyt = self.wyts[timestep.year]  # just calculate this as needed
        ferc_flow_req = self.ferc_req(timestep, self.wyt)

        # DAVIS-GRUNSKY AGREEMENT REQUIREMENT
        dga_flow_req = self.dga_requirement(timestep)

        # COWELL AGREEMENT REQUIREMENT
        ca_flow_req = self.ca_requirement(timestep, scenario_index)

        # The required flow is (greater of the Davis-Grunsky and FERC flows) + the Cowell Agreement entitlement
        return max(ferc_flow_req, dga_flow_req) + ca_flow_req

    def ferc_req(self, timestep, wyt):
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
                gauge_Shafer_ts = self.model.recorders['Near Shaffer Bridge_11271290/flow'].to_dataframe()
                self.nov_dec_mean = gauge_Shafer_ts[st_date:end_date].mean().values[0]
            if self.nov_dec_mean >= 4.25:  # If mean flow greater than eaual to 150 cfs, then atleast 100 cfs flow
                ferc_lic_flow = 2.83

        return ferc_lic_flow

    def dga_requirement(self, timestep):
        # Davis-Grunsky Agreement
        # Flow required from Nov to March - 180 to 220 cfs. Using average value of 200 cfs(5.66 cms)
        if timestep.month in (11, 12, 1, 2, 3):
            davis_grunsky_flow = 5.66
        else:
            davis_grunsky_flow = 0

        return davis_grunsky_flow

    def ca_requirement(self, timestep, scenario_index):
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

            flow_val = 0

            # Calculate the natural flow
            # Because this should depend on the current timestep's inflow, inflow data should be
            # loaded all at once, then replace prev_flow with flow

            flow_val = 0
            for j in range(1, 7):
                # Note: the following two are about equivalent in time. Which to use seems to be arbitrary.
                # flow_val += self.model.nodes['MER_0{} Headflow'.format(j)].max_flow.value(timestep, scenario_index)
                flow_val += self.model.parameters['MER_0{} Headflow/Runoff'.format(j)].value(timestep, scenario_index)

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

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


Requirement_Merced_R_below_Merced_Falls_PH.register()
print(" [*] Requirement_Merced_R_below_Merced_Falls_PH successfully registered")
