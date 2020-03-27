import pandas as pd
import numpy as np
import json

with open('Diversion USGS gauges.json') as f:
    gauges = json.load(f)

cols = ['C', 'D', 'BN', 'AN', 'W']
cols_full = ['Critical', 'Dry', 'Below Normal', 'Above Normal', 'Wet']
sjvi = pd.read_csv('./sjvi.csv', index_col=0, header=0)['Yr-type'].to_dict()

basins = ['stanislaus']
for basin in basins:
    path = '../../data/{} River/gauges/streamflow_cfs.csv'.format(basin.title())
    gauge_data = pd.read_csv(path, index_col=0, parse_dates=True)
    for gauge in gauges[basin]:
        data = gauge_data[[gauge['gauge']]] / 35.31 * 0.0864  # convert to mcm
        data['WY'] = [sjvi[d.year] for d in data.index]
        data['Day'] = [d.strftime('%j') for d in data.index]
        pivoted = pd.pivot_table(
            data.reset_index(),
            values=gauge['gauge'],
            index='Day',
            columns='WY',
            aggfunc=np.mean
        ).fillna(0)
        outpath = path = '../../data/{basin} River/management/BAU/Demand/{diversion} demand by WYT mcm.csv'.format(
            basin=basin.title(),
            diversion=gauge['name']
        )
        pivoted = pivoted[cols]
        pivoted.columns = cols_full
        pivoted.to_csv(outpath)


