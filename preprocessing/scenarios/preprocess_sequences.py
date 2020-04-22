import os
import shutil
import pandas as pd
import random
import matplotlib.pyplot as plt
from functools import partial
import multiprocessing as mp
from itertools import product

SEQ_NAME_TPL = 'N{:02}_S{:02}'

LIVNEH_RUNOFF_PATH = 'hydrology/historical/Livneh/runoff'

root_dir = os.environ['SIERRA_DATA_PATH']
basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']

dfs = []

fnf_tpl = '{}/{{basin}}/hydrology/historical/Livneh/preprocessed/full_natural_flow_annual_mcm.csv'.format(root_dir)

for basin in basins:
    basin_full_name = '{} River'.format(basin.title())
    fnf_path = fnf_tpl.format(basin=basin_full_name)
    df = pd.read_csv(fnf_path, index_col=0, header=0)
    dfs.append(df)

df = pd.concat(dfs, axis=1)
df = df.sum(axis=1)
df_sorted = df.sort_values()


def generate_sequences(n_dry, n_wet, n_dry_years, n_buffer_years, n_sequences):
    """
    This script creates a sequence of psuedo-random years pulled from
    the Livneh dataset to generate sequences of dry years sandwiched between wet years.

    IMPORTANT: Full natural flow must be precalculated for the Livneh dataset (see preprocess_hydrology.py)

    :param n_dry: The number of dry years to sample from.
    :param n_wet: The number of wet years to sample from.
    :param n_dry_years: Total number of drought years.
    :param n_buffer_years: Number of wet years to add to the end of the sequence.
    :param n_sequences: Total number of sequences to generate.
    :return:
    """

    dry_years = list(df_sorted[:n_dry].index)
    wet_years = list(df_sorted[-n_wet:].index)

    # random samples
    # random_years = pd.DataFrame()
    # random_values = pd.DataFrame()
    drought_years = pd.DataFrame()
    # drought_values = pd.DataFrame()

    # Seed the random number generator to generate pseudo-random numbers
    # This is needed for reproducability.
    random.seed(1)

    for i in range(n_sequences):
        # random sequences (control)
        # n_total_years = n_years + n_buffer_years
        # random_years_sequence = [all_years[random.randint(0, len(all_years) - 1)] for j in range(n_total_years)]
        # random_years[i] = random_years_sequence
        # random_values[i] = [df[y] for y in random_years_sequence]

        # drought sequences
        first_year = wet_years[random.randint(0, n_wet - 1)]
        middle_years = [dry_years[random.randint(0, n_dry - 1)] for j in range(n_dry_years)]
        last_years = [wet_years[random.randint(0, n_wet - 1)] for j in range(1 + n_buffer_years)]
        drought_years_sequence = [first_year] + middle_years + last_years

        # col = (n_dry_years, i)
        col = SEQ_NAME_TPL.format(n_dry_years, i + 1)
        drought_years[col] = [int(y) for y in drought_years_sequence]
        # drought_values[col] = [df[y] for y in drought_years_sequence]

    # random_values.plot()
    # drought_values.plot()

    # plt.show()
    # print('done!')
    # return random_years, drought_years
    return drought_years


def generate_runoff_from_sequence(df, basin, dry_years_length, sequence):
    sequence_name = SEQ_NAME_TPL.format(dry_years_length, sequence)
    print(basin, sequence_name)

    sequence = df[sequence_name].values

    root_dir = os.environ['SIERRA_DATA_PATH']

    full_basin_name = '{} River'.format(basin.title())
    basin_dir = os.path.join(root_dir, full_basin_name, LIVNEH_RUNOFF_PATH)
    sequence_dir = os.path.join(root_dir, full_basin_name, 'hydrology', 'sequences', sequence_name, 'runoff')
    if not os.path.exists(sequence_dir):
        os.makedirs(sequence_dir)
    water_years = None
    for filename in os.listdir(basin_dir):
        filepath = os.path.join(basin_dir, filename)
        df = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True)

        if water_years is None:
            water_years = list(map(lambda d: d.year if d.month <= 9 else d.year + 1, df.index))
        df['WY'] = water_years
        df2 = pd.DataFrame()
        for i, year in enumerate(sequence):
            try:
                year = int(year)
            except:
                continue
            year_df = df[df['WY'] == year]['flw'].copy()
            start_year = 2000 + i
            start_date = '{}-10-01'.format(start_year)
            end_date = '{}-09-30'.format(start_year + 1)
            idx = pd.date_range(start_date, end_date)

            # account for leap years by adding/deleting days at end of year
            if len(year_df) < len(idx):
                year_df.index = idx[:len(year_df)]
                year_df[idx[-1]] = year_df.iloc[-1]
            elif len(year_df) > len(idx):
                year_df.pop(year_df.index[-1])
                year_df.index = idx
            else:
                year_df.index = idx
            df2 = df2.append(year_df.to_frame())

        df2.index.name = 'date'
        outpath = os.path.join(sequence_dir, filename)
        df2.to_csv(outpath)

    return


def generate_runoff(n_dry, n_wet, n_dry_years_max, n_buffer_years, n_sequences):
    drought_dfs = []
    dry_years_lengths = range(1, n_dry_years_max + 1)
    sequences = []
    for n in dry_years_lengths:
        drought_df = generate_sequences(n_dry, n_wet, n, n_buffer_years, n_sequences)
        drought_dfs.append(drought_df)
        sequences.extend([(n, s) for s in range(1, n_sequences + 1)])

    drought_dfs = pd.concat(drought_dfs, axis=1)
    root_dir = os.environ["SIERRA_DATA_PATH"]
    outdir = os.path.join(root_dir, "common", "hydrology", "sequences")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    drought_path = os.path.join(outdir, 'drought_sequences.csv')
    drought_dfs.to_csv(drought_path)

    basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']

    # delete previous sequence folders
    for basin in basins:
        root_dir = os.environ['SIERRA_DATA_PATH']
        full_basin_name = '{} River'.format(basin.title())
        basin_dir = os.path.join(root_dir, full_basin_name, LIVNEH_RUNOFF_PATH)
        sequences_dir = os.path.join(root_dir, full_basin_name, 'hydrology', 'sequences')
        if os.path.exists(sequences_dir):
            shutil.rmtree(sequences_dir)
            os.makedirs(sequences_dir)

    num_cores = mp.cpu_count() - 1

    pool = mp.Pool(processes=num_cores)

    for basin, (dry_years_length, sequence) in product(basins, sequences):
        args = (drought_dfs, basin, dry_years_length, sequence)
        pool.apply_async(generate_runoff_from_sequence, args)

    pool.close()
    pool.join()

    return


if __name__ == '__main__':
    n_dry = 30
    n_wet = 10
    n_dry_years_max = 7
    n_buffer_years = 1  # tack on to end of sequence
    n_sequences = 5

    generate_runoff(n_dry, n_wet, n_dry_years_max, n_buffer_years, n_sequences)
