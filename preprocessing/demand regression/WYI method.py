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
        data['Day'] = data.index.strftime('%j')  # add day
        medians = data.groupby('Day').median()[gauge['gauge']] # get median
        median_fractions = medians / medians.sum()
        outpath = path = '../../data/{basin} River/Management/BAU/Demand/{diversion} median fraction.csv'.format(
            basin=basin.title(),
            diversion=gauge['name']
        )
        median_fractions.name = 'Annual fraction'
        median_fractions = median_fractions.round(4)
        median_fractions *= 1 / median_fractions.sum()
        median_fractions.to_csv(outpath, header=True)
