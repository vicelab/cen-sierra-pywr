import os
import pandas as pd
from itertools import product

# basins = ['stanislaus', 'merced', 'upper san joaquin', 'tuolumne']
basins = ['stanislaus', 'merced']
scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
scenarios += gcm_rcps

basin_scenarios = product(basins, scenarios)

for basin, scenario in basin_scenarios:
    print(basin, scenario)
    datadir = '../../data/{} River/scenarios/{}/runoff'.format(basin.title(), scenario)
    for filename in os.listdir(datadir):
        if '_cms.csv' in filename:
            print(filename)
            inpath = os.path.join(datadir, filename)
            outpath = inpath.replace('_cms', '_mcm')
            df = pd.read_csv(inpath, index_col=0, parse_dates=True, header=0)*0.0864
            df.to_csv(outpath)