from scripts.forecast_daily_to_monthly import create_forcasted_hydrology
from scripts.full_natural_flow import create_full_natural_flow

basins = ['upper san joaquin']

root_dir = '../data'

create_forcasted_hydrology(root_dir, basins=basins)
create_full_natural_flow(root_dir, basins=basins)