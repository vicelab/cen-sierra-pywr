import os
from os.path import join
import pandas as pd

run = 'full run 2019-12-12'
resultsdir = r'C:\Users\david\Box\CERC-WET\Task7_San_Joaquin_Model\Pywr models\results'
rundir = join(resultsdir, run)

hdfpath = join(rundir, 'results.h5')

basins = ['merced']
for basin in basins:
    basindir = join(rundir, basin)
    header = [0,1,2]
    for result in os.listdir(join(basindir, 'Livneh_P2009')):
        if '.h5' in result:
            continue
        dfs = []
        for scenario in os.listdir(basindir):
            if '.h5' in scenario:
                continue
            scendir = join(basindir, scenario)
            path = join(scendir, result)
            df = pd.read_csv(path, parse_dates=True, index_col=0, header=header, skiprows=0)
            df.name = scenario
            new_cols = [tuple([scenario] + list(col)) for col in df.columns]
            df.columns = pd.MultiIndex.from_tuples(new_cols)
            dfs.append(df)
        df = pd.concat(dfs, axis=1)
        key = result.split('.')[0]
        outpath = join(basindir, 'results.h5')
        df.to_hdf(outpath, key=key.replace(' ', '_'))

print('done!')