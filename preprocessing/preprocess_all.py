import os
from itertools import product
from datetime import datetime, timedelta
from preprocessing.scripts import create_forecasted_hydrology, create_full_natural_flow, \
    full_natural_flow_exceedance_forecast
from preprocessing.scripts import upper_san_joaquin as usj
# from preprocessing.scripts import stanislaus as stn

import pandas as pd

# basins = ['upper san joaquin']
basins = ['stanislaus']

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')

scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
# scenarios += gcm_rcps

tasks = ["post"]

basin_scenarios = list(product(basins, scenarios))

for basin, scenario in basin_scenarios:

    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    scenarios_path = os.path.join(basin_path, 'Scenarios')
    basin_preprocessed_path = os.path.join(scenarios_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:
        if basin == 'upper san joaquin':
            usj.disaggregate_SJN_09_subwatershed(scenarios_path, scenario)

    # preprocess hydrology
    if "main" in tasks:
        create_forecasted_hydrology(root_dir, basin=basin, scenario=scenario)
        create_full_natural_flow(root_dir, basin=basin, scenario=scenario)

    if "post" in tasks:

        if basin == 'stanislaus':
            full_natural_flow_exceedance_forecast(basin_preprocessed_path, scenario)

        # after processing hydrology
        if basin == 'upper san joaquin':
            usj.sjrrp_below_friant(basin_preprocessed_path, scenarios, 'full_natural_flow_annual_mcm.csv')
