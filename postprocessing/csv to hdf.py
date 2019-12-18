import os
from os.path import join
import pandas as pd

run = 'full run 2019-12-12'
resultsdir = r'C:\Users\david\Box\CERC-WET\Task7_San_Joaquin_Model\Pywr models\results'
outdir = r'C:\data'
rundir = join(resultsdir, run)

hdfpath = join(outdir, '{basin}.h5')

headers = {
    'merced': [0, 1, 2],
    'stanislaus': [0, 1]
}

basins = ['stanislaus']
for basin in basins:
    print(basin)
    basindir = join(rundir, basin)
    header = headers[basin]
    for result in os.listdir(join(basindir, 'Livneh_P2009')):
        print(result)
        dfs = []
        for scenario in os.listdir(basindir):
            scendir = join(basindir, scenario)
            path = join(scendir, result)
            df = pd.read_csv(path, parse_dates=True, index_col=0, header=header, skiprows=0)
            df.name = scenario
            new_cols = [tuple([scenario] + list(col)) for col in df.columns]
            df.columns = pd.MultiIndex.from_tuples(new_cols)
            dfs.append(df)
        df = pd.concat(dfs, axis=1, sort=True)
        key = result.split('.')[0]
        df.to_hdf(hdfpath.format(basin=basin), key=key.replace(' ', '_'))

print('done!')
