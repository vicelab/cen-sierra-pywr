import os
import pandas as pd
import numpy as np

basins = ['stanislaus', 'merced', 'upper san joaquin', 'tuolumne']


def calculate_sjvi(climate):
    root_dir = os.environ['SIERRA_DATA_PATH']
    dfs = []
    for basin in basins:
        full_basin_name = '{} River'.format(basin.title())
        path = os.path.join(root_dir, full_basin_name, 'hydrology', climate, 'preprocessed',
                            'full_natural_flow_daily_mcm.csv')
        df = pd.read_csv(path, index_col=0, header=0, parse_dates=True)
        dfs.append(df)

    df_maf = pd.concat(dfs, axis=1).sum(axis=1) / 1.2335 / 1e3

    sjvi = 3.5
    water_years = df_maf.resample('Y').sum().index.year
    sjvi_values = pd.Series(index=water_years, name='SJVI (maf)', dtype=np.float64)
    sjvi_values.index.name = 'Water Year'
    sjvi_values[water_years[0]] = sjvi
    for wy in water_years[1:]:
        apr_1 = '{}-04-01'.format(wy)
        jul_31 = '{}-07-31'.format(wy)
        oct_1 = '{}-10-01'.format(wy - 1)
        mar_31 = '{}-03-31'.format(wy)
        apr_jul_maf = df_maf[apr_1:jul_31].sum()
        oct_mar_maf = df_maf[oct_1:mar_31].sum()
        sjvi = 0.6 * apr_jul_maf + 0.2 * oct_mar_maf + 0.2 * sjvi
        sjvi_values[wy] = sjvi

    outpath = os.path.join(root_dir, 'common', 'hydrology', climate)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    sjvi_values.to_csv(os.path.join(outpath, 'SJVI.csv'))
    return


if __name__ == '__main__':
    calculate_sjvi('historical/Livneh')
