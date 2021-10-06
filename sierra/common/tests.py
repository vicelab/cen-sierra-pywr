import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from dateutil.relativedelta import relativedelta


def test_planning_model(model, save_results=True, months=12):
    start = model.timestepper.start
    end = model.timestepper.end

    dates = pd.date_range(start=start, end=end, freq='MS')  # MS = month start

    # now = datetime.now()
    for date in tqdm(dates[:3], ncols=80, disable=True):
        model.reset(start=date)
        stepnow = datetime.now()
        model.step()
        # print((datetime.now() - stepnow).total_seconds())
        if save_results and date == dates[0]:
            save_planning_results(model, months)

    # print('\nRunning portion complete in {} seconds'.format((datetime.now() - now).total_seconds()))
    # print('...done')
    return


def get_planning_dataframe(model):
    date = model.timestepper.current.datetime
    df = model.to_dataframe()
    # df.columns = df.columns.droplevel(1)
    series = df.loc[date]

    node_names = []
    months = []

    col_tuples = []
    for c in df.columns:
        parts = c[0].split('/')
        if len(parts) == 4:
            res_name, variable, block, month_str = parts
            res_name = '{}/{}'.format(res_name, block)
        elif len(parts) == 3:
            res_name, variable, month_str = parts
        else:
            continue
        month = date + relativedelta(months=int(month_str) - 1)
        var_name = '{}/{}'.format(res_name, variable)
        col_tuples.append(tuple([var_name, month]) + c[1:])
    df = pd.DataFrame(data=[series], index=[date])
    df.columns = pd.MultiIndex.from_tuples(col_tuples)
    # df0 = df_filtered.stack(level=0)
    df1 = df.stack(level=1)
    df1.index.names = ['Date', 'Planning Date']
    # df0.index.names = ['Start month', 'Resource']

    return df1
