import os
import shutil
import pandas as pd
import random
import multiprocessing as mp

from joblib import Parallel, delayed
from itertools import product

from preprocessing.preprocess_hydrology import preprocess_hydrology
from preprocessing.utils.sequences import generate_data_from_sequence

from sierra_cython.constants import basin_lookup

RND_SEQ_NAME_TPL = 'S{id:04}_Y{years:02}_RAND_N{number:02}'
DRY_SEQ_NAME_TPL = 'S{id:04}_Y{years:02}_D{dry:1}W{wet:1}_N{number:02}'

FLOW_HEADER = 'flow (mcm)'
LIVNEH_RUNOFF_PATH = 'hydrology/historical/Livneh/runoff'

root_dir = os.environ['SIERRA_DATA_PATH']
basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']
# basins = ['upper san joaquin']

dfs = []

fnf_tpl = '{}/{{basin}}/hydrology/historical/Livneh/preprocessed/full_natural_flow_annual_mcm.csv'.format(root_dir)

for basin in basins:
    basin_full_name = '{} River'.format(basin.title())
    fnf_path = fnf_tpl.format(basin=basin_full_name)
    df = pd.read_csv(fnf_path, index_col=0, header=0)
    dfs.append(df)

regional_runoff_df = pd.concat(dfs, axis=1)
regional_runoff_df = regional_runoff_df.sum(axis=1)

# remove the first and last years, which are not complete
regional_runoff_df.pop(df.index[0])
regional_runoff_df.pop(df.index[-1])
regional_runoff_sorted_df = regional_runoff_df.sort_values()


def generate_sequence(n_dry, n_wet, n_buffer_years, scenario_number, sequence_number, n_dry_years=0, n_wet_years=0,
                      n_years=0):
    """
    This script creates a sequence of psuedo-random years pulled from
    the Livneh dataset to generate sequences of dry years sandwiched between wet years.

    IMPORTANT: Full natural flow must be precalculated for the Livneh dataset (see preprocess_hydrology.py)

    :param n_dry: The number of dry years to sample from.
    :param n_wet: The number of wet years to sample from.
    :param n_dry_years: Total number of dry years.
    :param n_wet_years: Total number of wet years in between droughts.
    :param n_buffer_years: Number of wet years to add to the end of the sequence.
    :return:
    """

    dry_years = list(regional_runoff_sorted_df[:n_dry].index)
    wet_years = list(regional_runoff_sorted_df[-n_wet:].index)
    all_years = dry_years + wet_years

    # random samples
    # random_years = pd.DataFrame()
    # random_values = pd.DataFrame()
    sequence_df = pd.DataFrame()
    # drought_values = pd.DataFrame()

    first_year = wet_years[random.randint(0, n_wet - 1)]

    if n_years:
        # random sequences
        sequence = [first_year]
        sequence += [all_years[random.randint(0, n_dry + n_wet - 1)] for j in range(n_years)]
        col = RND_SEQ_NAME_TPL.format(id=scenario_number, years=n_years, number=sequence_number)

    else:

        # drought sequences
        middle_years_dry_1 = [dry_years[random.randint(0, n_dry - 1)] for j in range(n_dry_years)]
        middle_years_wet_1 = [wet_years[random.randint(0, n_wet - 1)] for j in range(n_wet_years)]
        middle_years_dry_2 = [dry_years[random.randint(0, n_dry - 1)] for j in range(n_dry_years)]
        middle_years = middle_years_dry_1 + middle_years_wet_1 + middle_years_dry_2
        last_years = [all_years[random.randint(0, n_wet + n_dry - 1)]]
        last_years += [all_years[random.randint(0, n_wet + n_dry - 1)]]
        sequence = [first_year] + middle_years + last_years

        years = len(sequence) - 1
        col = DRY_SEQ_NAME_TPL.format(id=scenario_number, years=years, dry=n_dry_years, wet=n_wet_years, number=sequence_number)
    sequence_df[col] = [int(y) for y in sequence]
    # drought_values[col] = [df[y] for y in drought_years_sequence]

    # random_values.plot()
    # drought_values.plot()

    # plt.show()
    # print('done!')
    # return random_years, drought_years
    return sequence_df


def generate_sequences_runoff(definition_path, outdir, basins_to_process=None, debug=False):

    sequences_df = pd.read_csv(definition_path, index_col=0, header=0)

    # sequence values
    # values_df = sequences_df.applymap(lambda x: regional_runoff_df[int(x)] if not pd.isna(x) else None)
    # values_df.to_csv(sequences_values_path)

    basins = basins_to_process or ['stn', 'tuo', 'mer', 'usj']

    # delete previous sequence folders
    for basin in basins:
        full_basin_name = basin_lookup[basin]['full name']
        # basin_dir = os.path.join(root_dir, full_basin_name, LIVNEH_RUNOFF_PATH)
        sequences_dir = os.path.join(root_dir, full_basin_name, 'hydrology', 'sequences')
        if os.path.exists(sequences_dir):
            shutil.rmtree(sequences_dir)
        
        os.makedirs(sequences_dir)

    all_args = []
    for basin, seq_id in product(basins, sequences_df.index):

        full_basin_name = basin_lookup[basin]['full name']
        basin_dir = os.path.join(root_dir, full_basin_name)
        sequence_dir = os.path.join(outdir, full_basin_name, 'hydrology', 'sequences', seq_id, 'runoff')
        seq_values = [v for v in sequences_df.loc[seq_id].values if not pd.isna(v)]

        args = (basin, 'runoff', seq_id, seq_values, basin_dir, sequence_dir)

        if debug:
            generate_data_from_sequence(*args)
        else:
            all_args.append(args)

    if not debug:
        num_cores = mp.cpu_count() - 1
        Parallel(n_jobs=num_cores)(delayed(generate_data_from_sequence)(*args) for args in all_args)

    return


if __name__ == '__main__':

    debug = True
    outdir = r'C:\Users\david\sierra\SynologyDrive\data'
    # outdir = root_dir
    generate_sequences_runoff(outdir, debug=debug)
    preprocess_hydrology('sequences', basins_to_process=['stn'], debug=debug)
