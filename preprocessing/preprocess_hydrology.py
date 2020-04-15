import os
from itertools import product
import preprocessing.hydrology.common as common
import preprocessing.hydrology.upper_san_joaquin as usj
import preprocessing.hydrology.stanislaus as stn
import preprocessing.hydrology.merced as mer

# import preprocessing.tuolumne as tuo

# basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']
basins = ["merced"]

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')

scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
scenarios += gcm_rcps

tasks = ["pre", "common", "basins"]
# tasks = ["basins"]

basin_scenarios = list(product(basins, scenarios))

for basin, scenario in basin_scenarios:
    print("\n Processing {}: {}\n".format(basin, scenario))
    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    scenarios_path = os.path.join(basin_path, 'scenarios')
    scenario_path = os.path.join(scenarios_path, scenario)
    preprocessed_path = os.path.join(scenario_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:
        if basin == 'upper san joaquin':
            usj.disaggregate_SJN_09_subwatershed(scenario_path)

    # preprocess hydrology
    if "common" in tasks:
        print("Aggregating subwatersheds...")
        common.aggregate_subwatersheds(scenario_path, basin)

        print("Creating forecasted hydrology...")
        common.create_forecasted_hydrology(scenario_path)

        print("Creating full natural flow...")
        src = os.path.join(scenario_path, 'runoff_aggregated')
        dst = preprocessed_path
        common.create_full_natural_flow(src, dst)

    if "basins" in tasks:

        if basin == 'stanislaus':
            stn.calculate_WYT_P2005_P2130(scenario_path)
            stn.calculate_WYT_P2019(scenario_path)
            stn.calculate_peak_donnell_lake_inflow(scenario_path)
            common.full_natural_flow_exceedance_forecast(scenario_path)  # only done for stanislaus for now

        elif basin == 'merced':
            mer.calculate_Exchequer_WYT(scenario_path)

        elif basin == 'upper san joaquin':
            src = dst = preprocessed_path
            usj.sjrrp_below_friant(src, dst)
            usj.calculate_millerton_snowmelt_inflow(src, dst)
