from dateutil.relativedelta cimport relativedelta
from calendar cimport monthrange

cimport pandas as pd
from pywr.parameters cimport Parameter


class Timestep(object):
    step = None
    datetime = None
    year = None
    month = None


class WaterLPParameter(Parameter):
    cpdef double cfs_to_cms = 1 / 35.315

    cdef char* mode = 'scheduling'
    cdef char* res_class = 'network'
    res_name = None
    res_name_full = None
    attr_name = None
    block = None
    month = None
    year = None
    days_in_month = None
    month_offset = None
    month_suffix = ''
    demand_constant_param = ''
    elevation_param = ''
    cdef int num_scenarios = 0

    timestep = Timestep()

    cpdef void setup(self):
        super().setup()

        self.num_scenarios = len(self.model.scenarios.combinations)

        self.mode = getattr(self.model, 'mode', self.mode)

        name_parts = self.name.split('/')
        self.res_name = name_parts[0]

        if len(name_parts) >= 2:
            self.attr_name = name_parts[1]
            self.res_attr_name = '/'.join(name_parts[:2])

        if self.mode == 'scheduling':
            if len(name_parts) == 3:

                # add the block number
                self.block = int(name_parts[2])

                # add/update the list of all blocks for the resource/attribute
                blocks = self.model.blocks.get(self.res_attr_name, []) + [self.block]
                self.model.blocks[self.res_attr_name] = sorted(blocks)
        else:
            if len(name_parts) >= 2:
                self.month_offset = int(name_parts[-1]) - 1
            if len(name_parts) == 4:

                # add the block number
                self.block = int(name_parts[-2])

                # add/update the list of all blocks for the resource/attribute
                blocks = self.model.blocks.get(self.res_name, []) + [self.block]
                self.model.blocks[self.res_attr_name] = sorted(blocks)

        if self.month_offset is not None:
            self.month_suffix = '/{}'.format(self.month_offset + 1)

        try:
            node = self.model.nodes[self.res_name + self.month_suffix]
        except:
            node = None

        if node and 'level' in node.component_attrs or self.attr_name == 'Storage Value':
            self.elevation_param = '{}/Elevation'.format(self.res_name) + self.month_suffix

    cpdef void before(self):
        super(WaterLPParameter, self).before()
        self.datetime = self.model.timestepper.current.datetime

        if self.model.mode == 'planning':
            if self.month_offset:
                self.datetime += relativedelta(months=+self.month_offset)

            self.year = self.datetime.year
            self.month = self.datetime.month

        if 4 <= self.datetime.month <= 12:
            self.operational_water_year = self.datetime.year
        else:
            self.operational_water_year = self.datetime.year - 1

        if self.datetime.day == 1:
            self.days_in_month = monthrange(self.datetime.year, self.datetime.month)[1]

    cpdef int get(self, param, timestep, scenario_index):
        return self.model.parameters[param].value(timestep, scenario_index)

    cpdef int[] get_days_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        return monthrange(year, month)[1]

    cpdef int[] get_dates_in_month(self, year=None, month=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        start = pd.datetime(year, month, 1)
        ndays = monthrange(year, month)[1]
        dates = pd.date_range(start, periods=ndays).tolist()
        return dates
