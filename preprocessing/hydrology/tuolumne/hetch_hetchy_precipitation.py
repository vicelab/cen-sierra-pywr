import os
import pandas as pd

from preprocessing.utils.sequences import generate_data_from_sequence
from sierra.utilities.constants import basin_lookup

root_dir = os.environ['SIERRA_DATA_PATH']


def hh_precip_from_Livneh(metadata_path, sequence_name, source_path, dest_path):
    filepath = os.path.join(metadata_path, 'sequence_definitions.csv')
    sequences_df = pd.read_csv(filepath, index_col=0, header=0)

    source_path = os.path.join(root_dir, 'Tuolumne River/hydrology/historical/Livneh/precipitation/')
    source_precip = pd.read_csv(source_path,'precipitation_Hetch_Hetchy_mm.csv', index_col=0, header=0, parse_dates=True)
    source_precip['date'] = source_precip.index.map(lambda d: d.year if d.month < 10 else d.year + 1)

    full_basin_name = 'Tuolumne River'
    basin_dir = os.path.join(root_dir, full_basin_name)

    sequence_dir = dest_path

    sequence = sequences_df.loc[sequence_name]
    sequence_values = [s for s in sequence.values if not pd.isna(s)]

    args = ('tuolumne', 'precipitation', sequence_values, basin_dir, sequence_dir)

    all_climates = []
    basin_climates = []
    basins = ['tuolumne']
    
    for basin in basins:
        
        full_basin_name = '{} River'.format(basin.title())

        dataset_dir = os.path.join(root_dir, full_basin_name, 'hydrology', 'sequences')
        for climate in os.listdir(dataset_dir):
            basin_climates.append((basin, climate))
                    # climates[dataset]
            all_climates.append(climate)

    generate_data_from_sequence(*args)
