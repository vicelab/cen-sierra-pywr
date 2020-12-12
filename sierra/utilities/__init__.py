from .network import simplify_network
from .planning import prepare_planning_model
from .schematics import create_schematic
from .results import save_model_results
from .tests import check_nan

from .constants import basin_lookup


class Basin(object):
    def __init__(self, basin_abbr):
        self.name = basin_lookup[basin_abbr]['name']
        self.full_name = basin_lookup[basin_abbr]['full name']
