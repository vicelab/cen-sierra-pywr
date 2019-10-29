from parameters import WaterLPParameter

from utilities.converter import convert


class IFR_bl_Hetch_Hetchy_Reservoir_Requirement(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):
        kwargs = dict(timestep=timestep, scenario_index=scenario_index)
        # ======
        # Base IFR
        # ======

        # get water year type
        wyt = self.get("IFR bl Hetch Hetchy Reservoir/Water Year Type", **kwargs)

        # get schedule
        schedule = self.model.parameters["IFR bl Hetch Hetchy Reservoir/IFR Schedule"].array()

        # get row & column
        row = timestep.month + 1
        if timestep.month == 9 and timestep.day >= 15 or timestep.month >= 10:
            row += 1
        col = [3, 2, 1].index(wyt) * 2 + 2
        if wyt == 1:
            col = 5

        base_ifr = schedule[row, col] + 5  # factor of safety based on practice

        ifr = base_ifr

        # 1987 Stipulation 1: +64 cfs if Kirkwood releases are > 920cfs
        if self.model.nodes['Canyon Power Tunnel'].flow[-1] > 920:
            ifr += 64

        # 1987 Stipulation 2: Additional blocks of water
        wyt = self.get("IFR bl Hetch Hetchy Reservoir/Water Year Type", **kwargs)
        if wyt < 3 and timestep.month in [5, 6, 7]:
            if wyt == 1:  # A
                block = 15000  # AF
            else:
                block = 6500
            wyt += block / 9 * 43560 / 10 / 24 / 3600
        elif wyt == 3 and timestep.month in [7, 8, 9]:
            block = 4400
            wyt += block / 9 * 43560 / 10 / 24 / 3600

        return ifr

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


IFR_bl_Hetch_Hetchy_Reservoir_Requirement.register()
print(" [*] IFR_bl_Hetch_Hetchy_Reservoir_Requirement successfully registered")