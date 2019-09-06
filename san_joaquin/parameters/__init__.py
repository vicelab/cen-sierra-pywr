import os
import pandas as pd
import redis
# from hashlib import md5

from pywr.parameters import Parameter

big_store = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, db=0)
big_store_type = 'redis'

class WaterLPParameter(Parameter):
    root_path = os.environ.get('ROOT_S3_PATH', '')
    store = {}

    def get(self, param, timestep=None, scenario_index=None):
        return self.model.parameters[param].value(timestep or self.model.timestep, scenario_index)

    def read_csv(self, *args, **kwargs):

        # hashval = md5((str(args) + str(kwargs)).encode()).hexdigest().encode()
        hashval = str(hash(str(args) + str(kwargs)))

        data = self.store.get(hashval)

        if data is None:
            if big_store_type == 'redis':
                data = big_store.get(hashval)
                if data:
                    data = pd.read_msgpack(data)
                    self.store[hashval] = data

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

            try:
                data = pd.read_csv(*args, **kwargs)
            except:
                print('Error reading file: {}'.format(args[0]))
                raise

            if big_store_type == 'redis':
                big_store.set(hashval, data.to_msgpack(compress='zlib'))
            else:
                big_store[hashval] = data
            self.store[hashval] = data

        return data

    def regression_hydropower_demand(self, timestep, scenario_index, demand_name, capacity):
        SJVI = self.get('WYI_SJValley', timestep=timestep, scenario_index=scenario_index)
        demand_regression = self.read_csv(
            'Management/BAU/Demand/Hydropower/{}.csv'.format(demand_name),
            header=None,
            skiprows=1,
            parse_dates=False,
            index_col=1,
        )
        m = demand_regression[2][min(timestep.datetime.weekofyear, 52)]
        b = demand_regression[3][min(timestep.datetime.weekofyear, 52)]
        return (m * SJVI + b) * capacity / 1e6
