import os
from itertools import product
import preprocessing.hydrology.common as common
import preprocessing.hydrology.upper_san_joaquin as usj
import preprocessing.hydrology.stanislaus as stn
import preprocessing.hydrology.merced as mer
import pandas as pd

import multiprocessing as mp

# import preprocessing.tuolumne as tuo

# datasets_to_process = ['historical', 'gcms']
datasets_to_process = ['sequences']
basins_to_process = ['stn', 'tuo', 'mer', 'usj']
# basins_to_process = ["usj"]

basins = {
    "stn": {
        "name": "stanislaus",
    },
    "tuo": {
        "name": "tuolumne",
    },
    "mer": {
        "name": "merced",
    },
    "usj": {
        "name": "upper san joaquin",
    },
}

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')

scenarios = {}

if 'historical' in datasets_to_process:
    scenarios['historical'] = ['Livneh']

if 'gcms' in datasets_to_process:
    gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
    rcps = ['45', '85']
    gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
    scenarios['gcms'] = gcm_rcps

if 'sequences' in datasets_to_process:
    sequences_path = os.path.join(root_dir, 'common/hydrology/sequences/drought_sequences.csv')
    seq_df = pd.read_csv(sequences_path, index_col=0, header=0)
    scenarios['sequences'] = seq_df.columns

tasks = ["pre", "common", "basins"]
# tasks = ["pre"]

scenario_paths = []
for k, values in scenarios.items():
    for v in values:
        scenario_paths.append('{}/{}'.format(k, v))

basin_scenarios = list(product(basins_to_process, scenario_paths))


def process_basin_scenario(basin, scenario):
    print("Processing {}: {}".format(basin, scenario))
    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    scenarios_path = os.path.join(basin_path, 'hydrology')
    scenario_path = os.path.join(scenarios_path, scenario)
    preprocessed_path = os.path.join(scenario_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:

        # print("Converting original cms runoff to mcm...")
        # abbr = b.upper() + 'R'
        # rel_src = '../bias correction/{abbr}/Catchment_RO_BC/{clim}'.format(abbr=abbr, clim=scenario)
        # src = os.path.join(root_dir, rel_src)
        # dst = os.path.join(scenario_path, 'runoff')
        #
        # if not os.path.exists(dst):
        #     os.makedirs(dst)
        #
        # common.convert_cms_to_mcm(src, dst)

        # if basin == 'tuolumne':
        #     print("Extracting precipitation at Hetch Hetchy...")
        #
        #     if scenario != 'Livneh':
        #         lat = -119.7739
        #         lon = 37.9491
        #         start = 2006
        #         end = 2099
        #         climate, rcp = scenario.split('_')
        #         src = os.path.join(root_dir, '..', 'precipitation', climate, rcp)
        #         dstdir = os.path.join(scenario_path, "precipitation")
        #         dst = os.path.join(dstdir, "rainfall_Hetch_Hetchy_mcm.csv")
        #         common.extract_precipitation_at(src, dst, lat, lon, start, end)

        if basin == 'upper san joaquin':
            # print("Disaggregating SJN_09 subwatershed...")
            usj.disaggregate_SJN_09_subwatershed(scenario_path)

    # preprocess hydrology
    if "common" in tasks:
        # print("Aggregating subwatersheds...")
        common.aggregate_subwatersheds(scenario_path, basin)

        # print("Creating forecasted hydrology...")
        common.create_forecasted_hydrology(scenario_path)

        # print("Creating full natural flow...")
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


if __name__ == '__main__':
    num_cores = mp.cpu_count() - 1
    pool = mp.Pool(processes=num_cores)
    print("Starting processing...")
    for b, scenario in basin_scenarios:
        basin = basins[b]['name']
        pool.apply_async(process_basin_scenario, (basin, scenario))

    pool.close()
    pool.join()

    print('done!')
