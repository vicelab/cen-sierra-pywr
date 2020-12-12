import os

from loguru import logger

from preprocessing.preprocess_sequences import generate_sequences_runoff
from preprocessing.preprocess_hydrology import preprocess_hydrology

# Preprocess sequences
# NOTE: This does not generate the sequence definitions.
# For now, the sequence definitions are created in a jupyter notebook found in
# "/sierra/development/scenarios/sequence generation" (not currently part of this repository)
# TODO: move the above to this repo?

debug = True
datadir = os.environ['SIERRA_DATA_PATH']
# outdir = datadir
outdir = r'C:\Users\david\sierra\SynologyDrive\data'

def preprocess_sequences():
    definition_path = os.path.join(datadir, 'metadata', 'sequence_definitions.csv')
    if not os.path.exists(definition_path):
        logger.error('{} not found'.format(definition_path))
        raise

    # basins = ['stn', 'tuo', 'mer', 'usj']
    basins = ['stn']

    generate_sequences_runoff(definition_path, outdir, basins_to_process=basins, debug=debug)
    #preprocess_hydrology('sequences', basins_to_process=basins, debug=debug)

logger.info('Finished preprocessing!')

if __name__ == '__main__':
    
    preprocess_sequences()