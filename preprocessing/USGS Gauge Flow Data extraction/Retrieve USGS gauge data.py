#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
DEBUG = False

# basin = 'merced'
# basin = 'upper san joaquin'
# basin = 'tuolumne'
basin = 'stanislaus'

# variable, pc = 'streamflow', '00060'
variable, pc = 'storage', '00054'

if not os.path.exists(basin):
    os.mkdir(basin)

gages = pd.read_excel('USGS gauges.xlsx', sheet_name='{} - {}'.format(basin, variable), header=None, squeeze=True)

dfs = []
if DEBUG:
    gages = gages[:3]
for i, gage in enumerate(gages):
    gage_number = gage.strip().split(' ')[1]
    print('retrieving {} ({}%)'.format(gage, int((i+1) / len(gages) * 100)))
    # https://waterservices.usgs.gov/rest/IV-Service.html
    payload = dict(
        format='json,1.1',
        parameterCd=pc,
        sites=[gage_number],
        startDT='1975-10-01',
        endDT='2018-09-30',
    )
    headers = {
        'Accept-encoding': 'gzip',
        'max-age': '120'
    }
    resp = requests.get('https://waterservices.usgs.gov/nwis/dv/?', params=payload, headers=headers)
    data = json.loads(resp.content.decode())
    values = data['value']['timeSeries']
    df = pandas
    for value in values:
        site_name =
    data = data['value']['timeSeries'][idxmx]['values'][0]['value']
    DF = pd.DataFrame(data, columns=['dateTime', 'value', 'qualifiers'])
    DF.index = pd.to_datetime(DF.pop('dateTime'))
    s = df[df.columns[0]]
    s.name = gage
    dfs.append(s)
df = pd.concat(dfs, axis=1)
df.index.name = 'Date'
if DEBUG:
    print(df.head())
    df.plot()
    plt.show()
else:
    if variable == 'storage':
        df = df * 1233.5 / 1e6
        path = '../../data/{} River/gauges/storage_mcm.csv'.format(basin.title())
        df.to_csv(path)
    else:
        path = '../../data/{} River/gauges/streamflow_cfs.csv'.format(basin.title())
        df.to_csv(path)
print('done!')


# In[ ]:




