#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
import shutil
from itertools import product


def create_forecasted_hydrology(scenario_path):

    # In[5]:

    DEFAULT_ALPHA = 0.2
    YEARS_OF_RECORD = 30

    alphas = {}  # Note: default is zero
    for m in range(1, 13):
        alphas[m] = {}
        if 3 >= m <= 9:  # Mar-Sep
            for m2 in range(m, 9 + 1):
                alphas[m][m2] = 0.5 if m == 3 else 0.9

    # Initial pre-processing
    debug = False
    month_columns = ['{:02}'.format(i) for i in range(1, 13)]

    runoff_dir = 'runoff_aggregated'
    runoff_dir_path = os.path.join(scenario_path, runoff_dir)
    #         print(runoff_dir)
    runoff_dir_monthly = runoff_dir_path.replace(runoff_dir, 'runoff_monthly')
    runoff_dir_monthly_forecasts = runoff_dir_path.replace(runoff_dir, 'runoff_monthly_forecasts')
    if os.path.exists(runoff_dir_monthly_forecasts):
        shutil.rmtree(runoff_dir_monthly_forecasts, ignore_errors=True)
    os.makedirs(runoff_dir_monthly_forecasts)
    filenames = os.listdir(runoff_dir_path)
    #     for filename in tqdm(os.listdir(runoff_dir), desc='{}, {}'.format(basin, scenario), ncols=800):
    for filename in filenames:
        if '.csv' not in filename:
            continue
        filepath = os.path.join(runoff_dir_path, filename)
        print(filepath)
        df = pd.read_csv(filepath, parse_dates=True, index_col=0)
        col = df.columns[0]

        # Aggregate to monthly
        df2 = df.groupby([lambda x: x.year, lambda x: x.month]).sum()
        df2.index.names = ['year', 'month']

        years = list(set(df2.index.get_level_values('year')))

        vals = []
        for i, (year, month) in enumerate(df2.index):

            # Monthly median
            start_year = max(year - YEARS_OF_RECORD, years[0])
            end_year = start_year + YEARS_OF_RECORD
            years_of_record = list(range(start_year, end_year + 1))
            index_slice = pd.IndexSlice[years_of_record, :]
            df3 = df2.loc[index_slice]
            df_median = df3.groupby('month').median()

            q_next = df2[col].iloc[i:i + 12].values
            if len(q_next) < 12:
                break

            next_months = [i + month for i in range(12)]
            next_months = [m if m < 13 else m - 12 for m in next_months]
            q_next_median = [df_median[col].loc[m] for m in next_months]

            # CORE FORECASTING ROUTINE
            next_months_qfcst = []
            for j, m in enumerate(next_months):
                alpha = alphas[month].get(m, DEFAULT_ALPHA)
                fcst = alpha * q_next[j] + (1 - alpha) * q_next_median[j]
                next_months_qfcst.append(fcst)

            vals.append(next_months_qfcst)

        index = pd.to_datetime(['{}-{}-01'.format(i[0], i[1]) for i in df2.index[:len(vals)]])
        df_final = pd.DataFrame(index=index, data=vals, columns=month_columns)
        df_final.index.name = 'Date'
        df_final.to_csv(os.path.join(runoff_dir_monthly_forecasts, filename))

        if debug:
            #             print(df3.head())
            #             fig, ax = plt.subplots(figsize=(12,5))
            #             df3.plot(ax=ax)
            #             plt.show()
            break
