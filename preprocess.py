import os

from loguru import logger

from preprocessing.preprocess_sequences import generate_sequences_runoff
from preprocessing.preprocess_hydrology import preprocess_hydrology

# Preprocess sequences
# NOTE: This does not generate the sequence definitions.
# For now, the sequence definitions are created in a jupyter notebook found in
# "/pywr_models/development/scenarios/sequence generation" (not currently part of this repository)
# TODO: move the above to this repo?

debug = True
# outdir = r'C:\Users\david\pywr_models\SynologyDrive\data'
datadir = os.environ['SIERRA_DATA_PATH']
outdir = datadir
definition_path = os.path.join(datadir, 'metadata', 'sequence_definitions.csv')
if not os.path.exists(definition_path):
    logger.error('{} not found'.format(definition_path))
    raise

basins = ['mer']

generate_sequences_runoff(definition_path, outdir, basins_to_process=basins, debug=debug)
#preprocess_hydrology('sequences', basins_to_process=basins, debug=debug)

logger.info('Finished preprocessing!')