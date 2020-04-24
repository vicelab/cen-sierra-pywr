import os
from itertools import product
import preprocessing.hydrology.common as common
import preprocessing.hydrology.upper_san_joaquin as usj
import preprocessing.hydrology.stanislaus as stn
import preprocessing.hydrology.merced as mer
import pandas as pd

import multiprocessing as mp

# import preprocessing.tuolumne as tuo

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')


def process_basin_climate(tasks, basin, climate):
    print("Processing {}: {}".format(basin, climate))
    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    hydrology_path = os.path.join(basin_path, 'hydrology')
    climate_path = os.path.join(hydrology_path, climate)
    preprocessed_path = os.path.join(climate_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:

        # print("Converting original cms runoff to mcm...")
        # abbr = b.upper() + 'R'
        # rel_src = '../bias correction/{abbr}/Catchment_RO_BC/{clim}'.format(abbr=abbr, clim=climate)
        # src = os.path.join(root_dir, rel_src)
        # dst = os.path.join(climate_path, 'runoff')
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
            usj.disaggregate_SJN_09_subwatershed(climate_path)

    # preprocess hydrology
    if "common" in tasks:
        # print("Aggregating subwatersheds...")
        common.aggregate_subwatersheds(climate_path, basin)

        # print("Creating forecasted hydrology...")
        common.create_forecasted_hydrology(climate_path)

        # print("Creating full natural flow...")
        src = os.path.join(climate_path, 'runoff_aggregated')
        dst = preprocessed_path
        common.create_full_natural_flow(src, dst)

    if "basins" in tasks:

        if basin == 'stanislaus':
            stn.calculate_WYT_P2005_P2130(climate_path)
            stn.calculate_WYT_P2019(climate_path)
            stn.calculate_peak_donnell_lake_inflow(climate_path)
            common.full_natural_flow_exceedance_forecast(climate_path)  # only done for stanislaus for now

        elif basin == 'merced':
            mer.calculate_Exchequer_WYT(climate_path)

        elif basin == 'upper san joaquin':
            src = dst = preprocessed_path
            usj.sjrrp_below_friant(src, dst)
            usj.calculate_millerton_snowmelt_inflow(src, dst)


def preprocess_hydrology(dataset, basins_to_process=None):

    basins_to_process = basins_to_process or ['stn', 'tuo', 'mer', 'usj']

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

    climates = {}

    if dataset == 'historical':
        climates['historical'] = ['Livneh']

    elif dataset == 'gcms':
        gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
        rcps = ['45', '85']
        gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
        climates['gcms'] = gcm_rcps

    elif dataset == 'sequences':
        sequences_path = os.path.join(root_dir, 'metadata/drought_sequences.csv')
        seq_df = pd.read_csv(sequences_path, index_col=0, header=0)
        climates['sequences'] = seq_df.index

    else:
        raise Exception("No dataset defined.")

    tasks = ["pre", "common", "basins"]
    # tasks = ["pre"]

    climate_paths = []
    for k, values in climates.items():
        for v in values:
            climate_paths.append('{}/{}'.format(k, v))

    basin_climates = list(product(basins_to_process, climate_paths))

    # basin-specific tasks; these can be parallelized
    debug = False
    if debug:
        for b, climate in basin_climates:
            basin = basins[b]['name']
            process_basin_climate(tasks, basin, climate)

    else:
        num_cores = mp.cpu_count() - 1
        pool = mp.Pool(processes=num_cores)
        print("Starting processing...")
        for b, climate in basin_climates:
            basin = basins[b]['name']
            pool.apply_async(process_basin_climate, (tasks, basin, climate))

        pool.close()
        pool.join()

    # common tasks
    for climate in climate_paths:
        common.calculate_sjvi(climate)

    print('done!')


if __name__ == '__main__':
    # datasets = ['historical', 'gcms']
    datasets = ['sequences']

    for dataset in datasets:
        preprocess_hydrology(dataset)
