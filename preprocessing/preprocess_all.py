import os
from itertools import product
from preprocessing.common import create_forecasted_hydrology, create_full_natural_flow, \
    full_natural_flow_exceedance_forecast, aggregate_subwatersheds
import preprocessing.upper_san_joaquin as usj
import preprocessing.stanislaus as stn
import preprocessing.merced as mer
# import preprocessing.tuolumne as tuo

basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')

scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
# scenarios += gcm_rcps

tasks = ["pre", "common", "basins"]

basin_scenarios = list(product(basins, scenarios))

for basin, scenario in basin_scenarios:

    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    scenarios_path = os.path.join(basin_path, 'scenarios')
    scenario_path = os.path.join(scenarios_path, scenario)
    basin_preprocessed_path = os.path.join(scenario_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:
        if basin == 'upper san joaquin':
            usj.disaggregate_SJN_09_subwatershed(scenario_path)

    # preprocess hydrology c
    if "common" in tasks:

        print("Aggregating subwatersheds...")
        aggregate_subwatersheds(root_dir, basin, scenario)

        print("Creating forecasted hydrology...")
        create_forecasted_hydrology(root_dir, basin, scenario, runoff_dir='runoff_aggregated')

        print("Creating full natural flow...")
        create_full_natural_flow(root_dir, basin, scenario)

    if "basins" in tasks:

        if basin == 'stanislaus':
            stn.wyts.calculate_WYT_P2005_P2130(scenario_path)
            stn.wyts.calculate_WYT_P2019(scenario_path)
            full_natural_flow_exceedance_forecast(scenario_path)

        # after processing hydrology
        if basin == 'upper san joaquin':
            usj.sjrrp_below_friant(scenario_path)
