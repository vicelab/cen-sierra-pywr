import os
from itertools import product

from preprocessing.scripts import create_forecasted_hydrology
from preprocessing.scripts import create_full_natural_flow
from preprocessing.scripts import upper_san_joaquin as usj

basins = ['upper san joaquin']
# basins = ['stanislaus']

root_dir = '../data'

scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
# scenarios += gcm_rcps

for basin in basins:

    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))

    # before processing hydrology
    if basin == 'upper san joaquin':
        scenarios_path = os.path.join(basin_path, 'Scenarios')
        usj.disaggregate_SJN_09_subwatershed(scenarios_path, scenarios)


    create_forecasted_hydrology(root_dir, basins=[basin], scenarios=scenarios)
    create_full_natural_flow(root_dir, basins=[basin], scenarios=scenarios)

    # after processing hydrology
    if basin == 'upper san joaquin':
        root_path = os.path.join(basin_path, 'Scenarios', 'preprocessed')
        # usj.sjrrp_below_friant(root_path, scenarios, 'full_natural_flow_annual_mcm.csv')
