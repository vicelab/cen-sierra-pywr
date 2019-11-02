from parameters import WaterLPParameter

from utilities.converter import convert


class TID_Demand(WaterLPParameter):
    """"""

    def _value(self, timestep, scenario_index):

        WYT_names = ["Critical", "Dry", "Below", "Above", "Wet"]
        WYT = WYT_names[self.model.parameters["WYT_SJValley"].value(timestep, scenario_index) - 1]
        date = timestep.datetime.strftime("%#m/%#d/") + "1900"

        return self.model.tables["TID_Demand"][WYT][date]

    def value(self, timestep, scenario_index):
        try:
            return convert(self._value(timestep, scenario_index), "ac-ft", "m^3", scale_in=1, scale_out=1000000)
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


TID_Demand.register()
print(" [*] TID_Demand successfully registered")
