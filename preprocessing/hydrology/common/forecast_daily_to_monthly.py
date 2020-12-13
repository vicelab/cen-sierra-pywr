#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pandas as pd
import shutil
from itertools import product


def create_forecasted_hydrology(scenario_path, dataset=None, default_alpha=0.2, nyears_of_record=30):
    alphas = {}  # Note: default is zero
    for m in range(1, 13):
        alphas[m] = {}
        if 3 >= m <= 9:  # Mar-Sep
            for m2 in range(m, 9 + 1):
                alphas[m][m2] = 0.5 if m == 3 else 0.9

    # Initial pre-processing

    debug = False
    # month_columns = ['{:02}'.format(i) for i in range(1, 13)]
    month_columns=['10', '11', '12', '01', '02', '03', '04', '05', '06' , '07', '08', '09']
    # get source runoff data
    runoff_dir = 'runoff_aggregated'
    scenario_runoff_dir_path = os.path.join(scenario_path, runoff_dir)
    if dataset in ['historical', 'gcms']:
        src_runoff_dir_path = scenario_runoff_dir_path
    else:
        src_runoff_dir_path = os.sep.join(scenario_path.split(os.sep)[:-2] + ['historical', 'Livneh', runoff_dir])
    src_runoff_filenames = os.listdir(src_runoff_dir_path)

    # create output data folder
    # runoff_dir_path = os.path.join(scenario_path, runoff_dir)
    #         print(runoff_dir)
    # runoff_dir_monthly = runoff_dir_path.replace(runoff_dir, 'runoff_monthly')
    runoff_dir_monthly_forecasts = os.path.join(scenario_path, 'runoff_monthly_forecasts')
    if os.path.exists(runoff_dir_monthly_forecasts):
        shutil.rmtree(runoff_dir_monthly_forecasts, ignore_errors=True)
    os.makedirs(runoff_dir_monthly_forecasts)

    months_to_calculate = None

    for runoff_filename in src_runoff_filenames:
        if '.csv' not in runoff_filename:
            continue
        src_path = os.path.join(src_runoff_dir_path, runoff_filename)
        print(src_path)
        df = pd.read_csv(src_path, parse_dates=True, index_col=0)
        col = df.columns[0]

        # Aggregate to monthly
        df2 = df.groupby([lambda x: x.year, lambda x: x.month]).sum()
        df2.index.names = ['year', 'month']

        if months_to_calculate is None:
            if dataset != 'sequences':
                months_to_calculate = list(df.index)
                # earliest_year = months_to_calculate[0][1]
                earliest_year = months_to_calculate[0]
            elif dataset == 'sequences':
                n_years = int(scenario_path.split('_Y')[1][:2])
                months_to_calculate = []
                for wy in range(2000, 2000 + n_years + 1):
                    for m in [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        y = wy - 1 if m >= 10 else wy
                        months_to_calculate.append((y, m))
                earliest_year = 2013 - nyears_of_record
            else:
                raise ('Routine not complete for dataset {}'.format(dataset))

        vals = []
        #        for i, (year, month) in enumerate(months_to_calculate):
        for i in range(len(months_to_calculate)):
            year = months_to_calculate[i].year
            month = months_to_calculate[i].month
            # Monthly median
            start_year = max(year - nyears_of_record, earliest_year.year)
            end_year = start_year + nyears_of_record
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
                alpha = alphas[month].get(m, default_alpha)
                fcst = alpha * q_next[j] + (1 - alpha) * q_next_median[j]
                next_months_qfcst.append(fcst)

            vals.append(next_months_qfcst)

        # index = pd.to_datetime(['{}-{}-01'.format(ym[0].year, ym[1].month) for i in range(len(months_to_calculate))])
        index1 = pd.to_datetime(['{}-{}-01'.format(months_to_calculate[i].year, months_to_calculate[i].month) for i in
                                 range(len(months_to_calculate))])
        index = index1.unique()
        # df_final = pd.DataFrame(index=index, data=vals, columns=month_columns)
        df_final = pd.DataFrame(index=index[9:-2], data=vals, columns=month_columns)
        df_final.index.name = 'Date'
        df_final.to_csv(os.path.join(runoff_dir_monthly_forecasts, runoff_filename))

        if debug:
            #             print(df3.head())
            #             fig, ax = plt.subplots(figsize=(12,5))
            #             df3.plot(ax=ax)
            #             plt.show()
            break
