import os
import pandas as pd
from hashlib import md5

from pywr.parameters import Parameter


class WaterLPParameter(Parameter):
    store = {}  # TODO: create h5 store on disk (or redis?) to share between class instances

    root_path = os.environ.get('ROOT_S3_PATH', '')

    # h5store = 'store.h5'

    def GET(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, param, timestep=None, scenario_index=None):
        return self.model.parameters[param].value(timestep or self.model.timestep, scenario_index)

    def read_csv(self, *args, **kwargs):

        # hashval = md5((str(args) + str(kwargs)).encode()).hexdigest()
        hashval = str(hash(str(args) + str(kwargs)))

        data = self.store.get(hashval)

        if data is None:

            if not args:
                raise Exception("No arguments passed to read_csv.")

            # update args with additional path information

            args = list(args)
            file_path = args[0]
            if '://' in file_path:
                pass
            elif self.root_path:
                args[0] = self.root_path + file_path

            # modify kwargs with sensible defaults
            # TODO: modify these depending on data type (timeseries, array, etc.)

            kwargs['parse_dates'] = kwargs.get('parse_dates', True)
            kwargs['index_col'] = kwargs.get('index_col', 0)

            data = pd.read_csv(*args, **kwargs)

            self.store[hashval] = data

        return data
