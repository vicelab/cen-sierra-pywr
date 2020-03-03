from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow(WaterLPParameter):
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

        date = self.datetime
        # get row & column
        lookup_row = date.month - 1
        month_day = (date.month, date.day)
        if month_day >= (9, 15):
            lookup_row += 1
        lookup_col = min([3, 2, 1].index(wyt) * 2 + 1, 4)

        base_ifr = schedule.iat[lookup_row, lookup_col] + 5  # factor of safety based on practice

        ifr = base_ifr

        # 1987 Stipulation 1: +64 cfs if Kirkwood releases are > 920 cfs
        if self.model.nodes["Kirkwood PH"].prev_flow * 35.315 > 920:
            ifr += 64

        # 1987 Stipulation 2: Additional blocks of water
        block_1987 = 0
        if wyt in [1, 2] and date.month in [5, 6, 7]:
            if wyt == 1:  # A
                block_1987 = 15000  # AF
            else:
                block_1987 = 6500
        elif wyt == 3 and date.month in [7, 8, 9]:
            block_1987 = 4400

        if block_1987:
            ifr += block_1987 / 90 / 24 / 3600 * 43560  # convert AF to cfs

        return ifr / 35.315

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "m^3 s^-1", "m^3 day^-1", scale_in=1,
                           scale_out=1000000.0)
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


IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow.register()
print(" [*] IFR_bl_Hetch_Hetchy_Reservoir_Min_Flow successfully registered")
