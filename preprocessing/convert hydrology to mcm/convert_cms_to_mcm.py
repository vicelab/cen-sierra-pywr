import os
import pandas as pd
from itertools import product

basins = ['stanislaus', 'merced', 'upper san joaquin', 'tuolumne']
climates = ['Livneh']

basin_climates = product(basins, climates)

for basin, climate in basin_climates:
    datadir = '../../data/{} River/Scenarios/{}/runoff'.format(basin.title(), climate)
    for filename in os.listdir(datadir):
        if '_cms.csv' in filename:
            print(filename)
            inpath = os.path.join(datadir, filename)
            outpath = inpath.replace('_cms', '_mcm')
            df = pd.read_csv(inpath, index_col=0, parse_dates=True, header=0)*0.0864
            df.to_csv(outpath)