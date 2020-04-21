import os
import pandas as pd
import random
import matplotlib.pyplot as plt


def generate_sequences(n_dry, n_wet, n_years, n_buffer_years, n_sequences):
    """
    This script creates a sequence of psuedo-random years pulled from
    the Livneh dataset to generate:
    1) sequences of random years pulled from the entire record and
    2) sequences of dry years sandwiched between wet years.

    :param n_dry: The number of dry years to sample from.
    :param n_wet: The number of wet years to sample from.
    :param n_years: Total length of the sequence of interest.
    :param n_buffer_years: Number of wet years to add to the end of the sequence.
    :param n_sequences: Total number of sequences to generate.
    :return:
    """
    root_dir = os.environ['SIERRA_DATA_PATH']

    basins = ['stanislaus', 'tuolumne', 'merced', 'upper san joaquin']

    dfs = []

    fnf_tpl = '{}/{{basin}}/scenarios/Livneh/preprocessed/full_natural_flow_annual_mcm.csv'.format(root_dir)

    for basin in basins:
        basin_full_name = '{} River'.format(basin.title())
        fnf_path = fnf_tpl.format(basin=basin_full_name)
        df = pd.read_csv(fnf_path, index_col=0, header=0)
        dfs.append(df)

    df = pd.concat(dfs, axis=1)
    df = df.sum(axis=1)
    df_sorted = df.sort_values()

    all_years = list(df.index)
    dry_years = list(df_sorted[:n_dry].index)
    wet_years = list(df_sorted[-n_wet:].index)

    dry_wet_years = dry_years + wet_years

    # random samples
    random_years = pd.DataFrame()
    random_values = pd.DataFrame()
    drought_years = pd.DataFrame()
    drought_values = pd.DataFrame()

    # Seed the random number generator to generate pseudo-random numbers
    # This is needed for reproducability.
    random.seed(1)

    for i in range(n_sequences):
        # random sequences (control)
        n_total_years = n_years + n_buffer_years
        random_years_sequence = [all_years[random.randint(0, len(all_years) - 1)] for j in range(n_total_years)]
        random_years[i] = random_years_sequence
        random_values[i] = [df[y] for y in random_years_sequence]

        # drought sequences
        n_dry_years = n_years - 2 - n_buffer_years
        first_year = wet_years[random.randint(0, n_wet - 1)]
        middle_years = [dry_years[random.randint(0, n_dry - 1)] for j in range(n_dry_years)]
        last_years = [wet_years[random.randint(0, n_wet - 1)] for j in range(1 + n_buffer_years)]
        drought_years_sequence = [first_year] + middle_years + last_years
        drought_years[i] = drought_years_sequence
        drought_values[i] = [df[y] for y in drought_years_sequence]

    random_values.plot()
    drought_values.plot()

    plt.show()
    print('done!')


if __name__ == '__main__':
    n_dry = 30
    n_wet = 10
    n_years = 7
    n_buffer_years = 1  # tack on to end of sequence
    n_sequences = 100

    generate_sequences(n_dry, n_wet, n_years, n_buffer_years, n_sequences)
