import os
import multiprocessing as mp

import argparse

from joblib import Parallel, delayed
from loguru import logger

import preprocessing.hydrology.common as common
import preprocessing.hydrology.stanislaus as stn
import preprocessing.hydrology.tuolumne as tuo
import preprocessing.hydrology.merced as mer
import preprocessing.hydrology.upper_san_joaquin as usj

from sierra_cython.utilities.constants import basin_lookup

# import preprocessing.tuolumne as tuo

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')
metadata_path = os.path.join(root_dir, 'metadata')


def process_basin_climate(tasks, basin, dataset, climate):
    print("Processing {}: {}/{}".format(basin, dataset, climate))

    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    hydrology_path = os.path.join(basin_path, 'hydrology')
    climate_path = os.path.join(hydrology_path, dataset, climate)
    preprocessed_path = os.path.join(climate_path, 'preprocessed')
    precipitation_path = os.path.join(climate_path, 'precipitation')

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

        if basin == 'tuolumne' and dataset == 'sequences':
            sequence_name = climate
            source_path = os.path.join(root_dir, 'Tuolumne River/hydrology/historical/Livneh/precipitation')
            dest_path = precipitation_path
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            try:
                tuo.hh_precip_from_Livneh(metadata_path, sequence_name, source_path, dest_path)
            except:
                logger.warning('Could not process Hetch Hetchy precipitation for {}'.format(dataset))

    # preprocess hydrology
    if "common" in tasks:
        # print("Aggregating subwatersheds...")
        common.aggregate_subwatersheds(climate_path, basin)

        # print("Creating forecasted hydrology...")
        # if dataset == 'historical':
        common.create_forecasted_hydrology(climate_path, dataset=dataset)

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


def preprocess_hydrology(dataset, basins_to_process=None, tasks=None, debug=False):
    basins_to_process = basins_to_process or ['stn', 'tuo', 'mer', 'usj']
    tasks = tasks or ["pre", "common", "basins"]

    climates = {}

    # if dataset == 'historical':
    #     climates['historical'] = ['Livneh']

    # elif dataset == 'gcms':
    #     # gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
    #     # rcps = ['45', '85']
    #     # gcm_rcps = ['_'.join(list(product(gcms, rcps)))]
    #     gcm_rcps = os.listdir()
    #     climates['gcms'] = gcm_rcps

    # elif dataset == 'sequences':
    #     sequences_path = os.path.join(root_dir, 'metadata/drought_sequences.csv')
    #     seq_df = pd.read_csv(sequences_path, index_col=0, header=0)
    #     climates['sequences'] = seq_df.index[:5] if debug else seq_df.index

    # else:
    #     raise Exception("No dataset defined.")

    all_climates = []
    basin_climates = []
    for basin in basins_to_process:
        full_basin_name = basin_lookup[basin]['full name']
        dataset_dir = os.path.join(root_dir, full_basin_name, 'hydrology', dataset)
        for climate in os.listdir(dataset_dir):
            basin_climates.append((basin, climate))
            # climates[dataset]
            all_climates.append(climate)

    # all_climates = []
    # for k, values in climates.items():
    #     for v in values:
    #         all_climates.append((k, v))

    # basin_climates = list(product(basins_to_process, all_climates))

    # basin-specific tasks; these can be parallelized
    if debug:
        for b, climate in basin_climates:
            basin = basin_lookup[b]['name']
            process_basin_climate(tasks, basin, dataset, climate)

    else:
        print("Starting processing...")
        num_cores = mp.cpu_count() - 1
        all_args = []
        for b, c in basin_climates:
            basin = basin_lookup[b]['name']
            args = (tasks, basin, dataset, c)
            all_args.append(args)

        Parallel(n_jobs=num_cores)(delayed(process_basin_climate)(*args) for args in all_args)

    # common tasks
    # NOTE: SJVI can only be calculated if all basins are preprocessed first!
    if len(basins_to_process) == 4:
        if debug:
            for climate in all_climates:
                common.calculate_sjvi('/'.join([dataset, climate]))
        else:
            dataset_climates = ['/'.join([dataset, climate]) for climate in all_climates]
            Parallel(n_jobs=num_cores)(
                delayed(common.calculate_sjvi)(dataset_climate) for dataset_climate in dataset_climates)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tasks",
                        help="Tasks to run. Options include 'pre', 'common', and 'basins'. Default is all.")
    parser.add_argument("-b", "--basin",
                        help="Basin to run. Options include 'stn', 'tuo', 'mer', and 'usj'. Default is all.")
    parser.add_argument("-d", "--dataset",
                        help="""
                        Hydrology dataset to preprocess. Options include 'historical', 'gcms', and 'sequences'. Default is None.
                        """)
    args = parser.parse_args()

    tasks = args.tasks or ["pre", "common", "basins"]
    basins = [args.basin] if args.basin else None
    dataset = args.dataset
    if not dataset:
        raise Exception('Dataset must be supplied')

    preprocess_hydrology(dataset, tasks=tasks, basins_to_process=basins, debug=True)
