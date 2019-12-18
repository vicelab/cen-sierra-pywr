#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
from itertools import product


def create_forcasted_hydrology(root_dir, basins=None):
    scenarios = ['Livneh']
    gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
    rcps = ['45', '85']
    gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
    scenarios += gcm_rcps

    basins = basins or ['stanislaus', 'upper san joaquin']

    # In[5]:

    alphas = {}
    for m in range(1, 13):
        alphas[m] = {}

        if m >= 3 and m <= 9:
            for m2 in range(m, 9 + 1):
                alphas[m][m2] = 0.5 if m == 3 else 1

    # Initial pre-processing
    debug = False
    month_columns = ['{:02}'.format(i) for i in range(1, 13)]
    basin_scenarios = list(product(basins, scenarios))
    for basin, scenario in basin_scenarios:
        print(basin, scenario)
        runoff_dir = os.path.join(root_dir, '{} River/Scenarios/runoff/{}'.format(basin.title(), scenario))
        #         print(runoff_dir)
        runoff_dir_monthly = runoff_dir.replace('runoff', 'runoff_monthly')
        runoff_dir_monthly_forecasts = runoff_dir.replace('runoff', 'runoff_forecasts')
        if not os.path.exists(runoff_dir_monthly):
            os.makedirs(runoff_dir_monthly)
        if not os.path.exists(runoff_dir_monthly_forecasts):
            os.makedirs(runoff_dir_monthly_forecasts)
        filenames = os.listdir(runoff_dir)
        #     for filename in tqdm(os.listdir(runoff_dir), desc='{}, {}'.format(basin, scenario), ncols=800):
        for filename in filenames:
            if '_mcm' not in filename:
                continue
            filepath = os.path.join(runoff_dir, filename)
            print(filepath)
            df = pd.read_csv(filepath, parse_dates=True, index_col=0)
            col = df.columns[0]

            # Aggregate to monthly
            df2 = df.groupby([lambda x: x.year, lambda x: x.month]).sum()
            df2.index.names = ['year', 'month']

            # Monthly mean
            df_mean = df2.groupby('month').mean()
            #             print(df_mean)

            vals = []
            for i, (year, month) in enumerate(df2.index):
                qnext = df2[col].iloc[i:i + 12].values
                if len(qnext) < 12:
                    break

                next_months = [i + month for i in range(12)]
                next_months = [m if m < 13 else m - 12 for m in next_months]
                qnext_avg = [df_mean[col].loc[m] for m in next_months]

                # CORE FORECASTING ROUTINE
                next_months_qfcst = []
                for j, m in enumerate(next_months):
                    alpha = alphas[month].get(m, 0)
                    fcst = alpha * qnext[j] + (1 - alpha) * qnext_avg[j]
                    next_months_qfcst.append(fcst)

                vals.append(next_months_qfcst)

            index = pd.to_datetime(['{}-{}-01'.format(i[0], i[1]) for i in df2.index[:len(vals)]])
            df3 = pd.DataFrame(index=index, data=vals, columns=month_columns)
            df3.index.name = 'Date'
            df3.to_csv(os.path.join(runoff_dir_monthly_forecasts, filename))

            if debug:
                #             print(df3.head())
                #             fig, ax = plt.subplots(figsize=(12,5))
                #             df3.plot(ax=ax)
                #             plt.show()
                break


if __name__ == '__main__':
    # basins = ['stanislaus', 'upper san joaquin']
    basins = ['upper san joaquin']
    create_forcasted_hydrology(basins=basins)
