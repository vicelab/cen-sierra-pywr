from sierra.base_parameters import MinFlowParameter

from sierra.utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Base_Flow(MinFlowParameter):
    """"""

    def _value(self, timestep, scenario_index):

        # Note: all IFR units are cfs

        # ======
        # Base IFR
        # ======

        # get water year type
        wyt = self.get("IFR bl Hetch Hetchy Reservoir/Water Year Type", timestep, scenario_index)

        # get schedule
        schedule = self.model.tables["IFR bl Hetch Hetchy Reservoir/IFR Schedule"]

        month = self.datetime.month
        day = self.datetime.day
        # get row & column
        lookup_row = month - 1
        month_day = (month, day)
        if month_day >= (9, 15):
            lookup_row += 1
        lookup_col = min([3, 2, 1].index(wyt) * 2 + 1, 4)

        base_ifr = schedule.iat[lookup_row, lookup_col] + 5  # factor of safety based on practice

        ifr_cfs = base_ifr

        # 1987 Stipulation 1: +64 cfs if Kirkwood releases are > 920 cfs
        if self.model.nodes["Kirkwood PH"].prev_flow[scenario_index.global_id] / 0.0864 * 35.315 > 920:
            ifr_cfs += 64

        # 1987 Stipulation 2: Additional blocks of water
        block_1987_af = 0
        if wyt in [1, 2] and month in [5, 6, 7]:
            if wyt == 1:  # A
                block_1987_af = 15000  # AF
            else:
                block_1987_af = 6500
        elif wyt == 3 and month in [7, 8, 9]:
            block_1987_af = 4400

        ifr_cfs += block_1987_af * 0.0056  # convert to cfs

        ifr_cms = ifr_cfs / 35.315

        return ifr_cms

    def value(self, timestep, scenario_index):
        val = self.requirement(timestep, scenario_index, default=self._value)
        return convert(val, "m^3 s^-1", "m^3 day^-1", scale_in=1, scale_out=1000000.0)

    @classmethod
    def load(cls, model, data):
        try:
            return cls(model, **data)
        except Exception as err:
            print('File where error occurred: {}'.format(__file__))
            print(err)
            raise


IFR_bl_Hetch_Hetchy_Reservoir_Base_Flow.register()
