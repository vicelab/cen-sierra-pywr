import os
import pandas as pd

from preprocessing.utils.sequences import generate_data_from_sequence

root_dir = os.environ['SIERRA_DATA_PATH']


def hh_precip_from_Livneh(metadata_path, sequence_name, source_path, dest_path):
    filepath = os.path.join(metadata_path, 'drought_sequences.csv')
    sequences_df = pd.read_csv(filepath, index_col=0, header=0)

    filename = 'precipitation_Hetch_Hetchy_mm.csv'

    source_filepath = os.path.join(source_path, filename)
    source_precip = pd.read_csv(source_filepath, index_col=0, header=0, parse_dates=True)
    source_precip['WY'] = source_precip.index.map(lambda d: d.year if d.month < 10 else d.year + 1)

    full_basin_name = 'Tuolumne River'
    basin_dir = os.path.join(root_dir, full_basin_name)

    sequence_dir = dest_path

    sequence = sequences_df.loc[sequence_name]
    sequence_values = [s for s in sequence.values if not pd.isna(s)]

    args = ('tuolumne', 'precipitation', sequence_values, basin_dir, sequence_dir)
    generate_data_from_sequence(*args)
