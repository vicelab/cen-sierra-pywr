import os
import pandas as pd
from calendar import monthrange
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from hashlib import md5

from pywr.parameters import Parameter


class WaterLPParameter(Parameter):
    store = {}  # TODO: create h5 store on disk (or redis?) to share between class instances

    root_path = os.environ.get('ROOT_S3_PATH')

    # h5store = 'store.h5'

    mode = 'scheduling'
    res_class = 'network'
    res_name = None
    res_name_full = None
    attr_name = None
    block = None
    month = 0
    month_offset = 0
    month_suffix = ''
    demand_constant_param = ''
    elevation_param = ''

    def setup(self):
        super(WaterLPParameter, self).setup()

        self.mode = getattr(self.model, 'mode', self.mode)

        name_parts = self.name.split('/')
        res_class = name_parts[0]

        if res_class in ['link', 'node']:
            self.res_class = name_parts[0]
            self.res_name = name_parts[1]
            self.attr_name = name_parts[2]
            self.res_name_full = '{} [{}]'.format(self.res_name, res_class)

            if self.mode == 'scheduling':
                if len(name_parts) == 4:
                    self.block = int(name_parts[3])

            elif self.mode == 'planning':
                if len(name_parts) == 4:
                    self.month = int(name_parts[3])
                elif len(name_parts) == 5:
                    self.month = int(name_parts[3])
                    self.block = int(name_parts[4])
                if self.month:
                    self.month_offset = self.month - 1

            if self.month:
                self.month_suffix = '/{}'.format(self.month)

            self.res_name_full += self.month_suffix

            node = None
            try:
                node = self.model.nodes[self.res_name_full]
            except:
                pass

            if node:

                if ' PH' in node.name:
                    self.demand_constant_param = "node/{}/Demand Constant".format(self.res_name)

                if 'level' in node.component_attrs:
                    self.elevation_param = 'node/{}/Elevation'.format(self.res_name)
                    if self.month:
                        self.elevation_param += self.month_suffix

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
            print(Exception)
            return timestep.datetime

    def days_in_planning_month(self, timestep, month_offset=0):
        date = self.planning_date(timestep, month_offset)
        return monthrange(date.year, date.month)[1]

    def dates_in_planning_month(self, timestep, month_offset=0):
        today = self.planning_date(timestep, month_offset)
        ndays = monthrange(today.year, today.month)[1]
        dates = pd.date_range(today, periods=ndays).tolist()
        return dates

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
                if '://' in self.root_path:
                    args[0] = os.path.join(self.root_path, file_path)
                else:
                    args[0] = os.path.join(self.root_path, self.model.metadata['title'], file_path)

            # modify kwargs with sensible defaults
            # TODO: modify these depending on data type (timeseries, array, etc.)

            kwargs['parse_dates'] = kwargs.get('parse_dates', True)
            kwargs['index_col'] = kwargs.get('index_col', 0)

            # Import data from local files
            # data = pd.read_csv("s3_imports/" + args[0].split('/').pop(), **kwargs)

            # Import data
            # print(args)
            try:
                data = pd.read_csv(*args, **kwargs)
            except:
                print(args)
                raise

            # Saving Data from S3 to a local directory
            # data.to_csv("s3_imports/" + args[0].split('/').pop(), header=True)

            self.store[hashval] = data

        return data

