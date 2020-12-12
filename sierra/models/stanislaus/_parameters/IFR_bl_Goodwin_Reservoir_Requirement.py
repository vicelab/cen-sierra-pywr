from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Goodwin_Reservoir_Requirement(MinFlowParameter):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _value(self, timestep, scenario_index):
        WYT = self.get('New Melones Lake/Water Year Type' + self.month_suffix, timestep, scenario_index)
        if WYT == 0:
            return 0
        schedule = self.model.tables["IFR bl Goodwin Dam schedule"]
        start = '{:02}-{:02}'.format(self.datetime.month, self.datetime.day)
        if self.model.mode == 'scheduling':
            min_ifr_cms = schedule.at[start, WYT] / 35.31  # cfs to cms
            # min_ifr = self.get_down_ramp_ifr(timestep, scenario_index, min_ifr, initial_value=200 / 35.31, rate=0.02)
            # if self.datetime.day in (1, 15):
            #     min_ifr = self.get_down_ramp_ifr(timestep, scenario_index, min_ifr, initial_value=200 / 35.31, rate=0.25)
            # elif timestep.index > 0:
            #     min_ifr = self.model.nodes[self.res_name].prev_flow[scenario_index.global_id] / 0.0864

        else:
            end = '{:02}-{:02}'.format(self.datetime.month, self.days_in_month)
            min_ifr_cms = schedule[WYT][start:end].mean() / 35.31  # cfs to cms

        # # Check if New Melones filled; if so, add a little more to manage reservoir
        # if self.model.mode == 'scheduling':
        #
        #     # get previous storage
        #     NML = self.model.nodes["New Melones Lake"]
        #     prev_storage_mcm = NML.volume[scenario_index.global_id]
        #     max_storage = NML.max_volume
        #
        #     if not self.NML_did_fill and prev_storage_mcm >= max_storage * 0.95:
        #         self.NML_did_fill = True
        #     # Let's also release extra if the reservoir filled and release slowly to a target storage of 2000 TAF by Oct 31.
        #     # This is based on observation, though need to confirm
        #     if self.NML_did_fill and (7, 1) <= (month, day) <= (10, 31) and prev_storage_mcm / 1.2335 >= 2000:
        #         # reservoir late summer drawdown is ~40.6 cms (350 TAF over Jul-Oct)
        #         min_ifr_cms = max(min_ifr_cms, 40.6)

        return min_ifr_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        return cls(model, **data)


IFR_bl_Goodwin_Reservoir_Requirement.register()
