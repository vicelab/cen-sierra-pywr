import os
import pandas as pd
from calendar import monthlen
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from hashlib import md5

from pywr.parameters import Parameter


class WaterLPParameter(Parameter):
    store = {}  # TODO: create h5 store on disk (or redis?) to share between class instances

    root_path = os.environ.get('ROOT_S3_PATH', '')

    # h5store = 'store.h5'

    def setup(self):
        super(WaterLPParameter, self).setup()
        self.mode = getattr(self.model, 'mode', 'scheduling')

    def GET(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, param, timestep=None, scenario_index=None):
        return self.model.parameters[param].value(timestep or self.model.timestep, scenario_index)

    def planning_date(self, timestep, month_offset=0):
        try:
            # month_offset = int(self.mode == 'planning' and self.name.split('/')[-1])
            future_date = timestep.datetime + relativedelta(months=+month_offset)
            return future_date
        except Exception:
            # print(Exception)
            return timestep.datetime

    def days_in_planning_month(self, timestep, month_offset=0):
        date = self.planning_date(timestep, month_offset)
        return monthlen(date.year, date.month)

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

            # Import data from local files
            data = pd.read_csv("s3_imports/" + args[0].split('/').pop(), **kwargs)

            # Import files from the S3 Bucket
            # data = pd.read_csv(*args, **kwargs)

            # Saving Data from S3 to a local directory
            # data.to_csv("s3_imports/" + args[0].split('/').pop(), header=True)

            self.store[hashval] = data

        return data


class CostParameter(WaterLPParameter):
    path = "s3_imports/energy_netDemand.csv"

    def get_cost(self, timestep, scenario_index, piece, demand_param):
        data = self.read_csv(self.path, index_col=0, parse_dates=True)

        totDemand, maxDemand, minDemand = data.loc[timestep.datetime]
        minVal = self.model.parameters[demand_param].value(timestep, scenario_index) * (
                totDemand / 768)  # 768 GWh is median daily energy demand for 2009
        maxVal = minVal * (maxDemand / minDemand)
        d = maxVal - minVal
        return -(maxVal - (piece * 2 - 1) * d / 8)
