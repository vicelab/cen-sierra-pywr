import os
from ast import literal_eval
import pandas as pd
import numpy as np
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from hashlib import md5

from pywr.parameters import Parameter


class NumpyArray(Parameter):
    def __init__(self, model, value, **kwargs):
        # called once when the parameter is created
        super().__init__(model, **kwargs)
        if type(value) == str:
            value = literal_eval(value)
        self._value = np.array(value, dtype=object)

    def array(self, row=None, col=None):
        if row is None and col is None:
            return self._value
        else:
            return 0

    def value(self, timestep=None, scenario_index=None):
        # called once per timestep for each scenario
        return 0

    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        value = data.pop("value", None)
        data.pop("comment", None)
        return cls(model, value, **data)

NumpyArray.register()  # register the name so it can be loaded from JSON
print(' [*] NumpyArray parameter registered')

def monthlen(year, month):
    return monthrange(year, month)[1]


class Timestep(object):
    step = None
    datetime = None
    year = None
    month = None


class WaterLPParameter(Parameter):
    store = {}  # TODO: create h5 store on disk (or redis?) to share between class instances

    root_path = os.environ.get('ROOT_S3_PATH')

    # h5store = 'store.h5'

    cfs_to_cms = 1 / 35.315

    mode = 'scheduling'
    res_class = 'network'
    res_name = None
    res_name_full = None
    attr_name = None
    block = None
    month = None
    year = None
    month_offset = None
    month_suffix = ''
    demand_constant_param = ''
    elevation_param = ''

    timestep = Timestep()

    def setup(self):
        super(WaterLPParameter, self).setup()

        self.mode = getattr(self.model, 'mode', self.mode)

        name_parts = self.name.split('/')
        self.res_name = name_parts[0]

        if len(name_parts) >= 2:
            self.attr_name = name_parts[1]

        if self.mode == 'scheduling':
            if len(name_parts) == 3:
                self.block = int(name_parts[2])
        else:
            if len(name_parts) == 3:
                self.month_offset = int(name_parts[-1]) - 1
            elif len(name_parts) == 4:
                self.block = int(name_parts[3])
                self.month_offset = int(name_parts[2]) - 1
            # if self.month_offset is not None:
            #     self.res_name = '{}/{}'.format(name_parts[0], self.month_offset + 1)

        if self.month_offset is not None:
            self.month_suffix = '/{}'.format(self.month_offset + 1)

        try:
            node = self.model.nodes[self.res_name + self.month_suffix]
        except:
            node = None

        if node and 'level' in node.component_attrs or self.attr_name == 'Storage Value':
            self.elevation_param = '{}/Elevation'.format(self.res_name) + self.month_suffix

    def before(self):
        super(WaterLPParameter, self).before()
        if self.mode == 'planning':
            if self.month_offset:
                datetime = self.model.timestepper.current.datetime + relativedelta(months=+self.month_offset)
            else:
                datetime = self.model.timestepper.current.datetime

            self.datetime = datetime
            self.year = datetime.year
            self.month = datetime.month

    def GET(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, param, timestep=None, scenario_index=None):
        return self.model.parameters[param].value(timestep or self.model.timestep, scenario_index)

    def days_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return monthrange(year, month)[1]

    def dates_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        start = pd.datetime(year, month, 1)
        ndays = monthrange(year, month)[1]
        dates = pd.date_range(start, periods=ndays).tolist()
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

