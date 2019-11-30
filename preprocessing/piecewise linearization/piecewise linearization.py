#!/usr/bin/env python
# coding: utf-8

# Note: This is derived from https://realpython.com/linear-regression-in-python/

# In[1]:


# get_ipython().run_line_magic('matplotlib', 'inline')

import csv
import datetime as dt
from calendar import monthrange, isleap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def days_in_month(year, month):
    return monthrange(year, month)[1]


# In[2]:


def rnd(x, n):
    return round(x * pow(10, n)) / pow(10, n)


# In[3]:


def ss(x, y):
    return np.sum((x - y) ** 2)


# ## Main processing

# ### Key functions
# 
# `get_split`: This is a basic function that splits a series of x-y pairs into two. It finds the split between an initial lower bound and upper bound (x_min and x_max, respectively) by finding the two contiguous subsets of y that minimize the squared difference between the sum of squares associated with the two sets.
# 
# `get_splits`: This function uses `get_split` to recursively subsplit a series. It currently can only divide by two. I.e., there must be either 1, 2, 4, 8, etc. total number of pieces as a result of the split. This is defined by `max_k` (as in 2^k), which is the square of two associated with the desired total number of pieces.

# In[4]:


def get_split(x, y, min_split=None, max_split=None, debug=False, trial='Demo'):
    predictions = []
    stats = []
    objs = []
    splits = []
    cnt = 0
    if len(x) == 0 or len(y) == 0:
        #         print('returning nothing for trial {}, because...'.format(trial))
        #         if len(x) == 0:
        #             print('x:', x)
        #         if len(y) == 0:
        #             print('y:', y)

        return None

    lb = min(x)
    ub = max(x)
    split = (ub + lb) / 2
    if min_split:
        split = max(split, min_split)
    if max_split:
        split = min(split, max_split)
    best_split = None
    old_split = 1e6
    tol = 0.025
    old_obj = 1e6
    best_obj = 1e6
    best_objs = []
    search_complete = False
    best_idx = None

    #     if debug:
    #         print('STARTING INFO:')
    #         print('split:', split)
    #         print('xmin:', min(x))
    #         print('lb:', lb)
    #         print('ub:', ub)

    while not search_complete and cnt < 15:
        cnt += 1
        splits.append(rnd(split, 1))
        #         if debug:
        #             print('split:', split)
        #             print('xmin:', min(x))
        #             print('lb:', lb)
        x1 = np.array([_x for _x in x if _x <= split])
        l1 = len(x1)
        l2 = len(x) - l1
        x2 = np.array(x[-l2:])

        y1 = np.array(y[:l1])
        y2 = np.array(y[l1:])

        # if len(y1) < 2 or len(y2) < 2:
        #     #             search_complete = True
        #     #             return best_split
        #     print(split)

        p1 = np.full(l1, y1.mean())
        p2 = np.full(l2, y2.mean())

        ss1 = ss(y1, p1)
        ss2 = ss(y2, p2)

        obj = (ss1 - ss2) ** 2
        best_obj = min(obj, best_obj)
        if best_obj < old_obj:
            best_split = split
            best_idx = l1
        #         if best_obj in best_objs:
        #             print('best_obj', best_obj)
        #             print(best_objs)
        #             break # we've been here before
        #         best_objs.append(best_obj)

        old_obj = obj
        rel_diff = abs((split - old_split) / old_split)
        #         print('relative difference:', rel_diff)
        #     print('old_obj', old_obj)
        #     print('obj', obj)
        if rel_diff <= tol:
            #         print(obj_diff / old_obj, tol)
            search_complete = True
        else:
            old_split = split
            if ss1 < ss2:  # look higher
                lb = split
                split += (ub - split) / 2
            else:  # look lower
                ub = split
                split -= (split - lb) / 2
            if min_split:
                split = max(split, min_split)
            if max_split:
                split = min(split, max_split)

        objs.append(rel_diff)
        stats.append((rnd(ss1, 3), rnd(ss2, 3)))
        predictions.append(((x1, p1), (x2, p2)))

    if debug:
        n = len(predictions)

        if debug:
            fig1, axes = plt.subplots(n, 1, figsize=(8, 3 * n))
            for i, predictionset in enumerate(predictions):
                ax = axes[i]
                ax.plot(x, y, label='Original prices')
                for j, (xp, yp) in enumerate(predictionset):
                    ax.plot(xp, yp, label='Piece {}, SS={}'.format(j + 1, stats[i][j]))
                ax.set_xlabel('Percent of day')
                ax.set_ylabel('Price ($/GWh?)')
                ax.set_title('Split = {}%'.format(splits[i]))
                ax.legend(loc='lower left')
                ax.axvline(splits[i], color='black', linestyle='dashed')
            plt.tight_layout()
            fig1.savefig('demo search steps - {}.png'.format(trial))

        fig2, ax = plt.subplots(figsize=(8, 3))
        ax.plot(x, y, label='Original prices')
        for j, (xp, yp) in enumerate(predictions[-1]):
            ax.plot(xp, yp, label='Piece {}, SS={}'.format(j + 1, stats[-1][j]))
        ax.set_xlabel('Percent of period')
        ax.set_ylabel('Price ($/GWh?)')
        ax.set_title('{} Final split = {}%'.format(trial, splits[-1]))
        ax.legend(loc='lower left')
        plt.tight_layout()
        fig2.savefig('demo final search step - {}.png'.format(trial))

        if debug:
            fig3, ax = plt.subplots(figsize=(6, 4))
            ax.plot(objs)
            ax.set_ylabel('Split difference (tol={:03})'.format(tol))
            ax.set_xlabel('Iteration')
            ax.set_title('{} Solution Convergence'.format(trial))
            ax.axhline(tol, color='black', linestyle='dashed')
            plt.tight_layout()
            fig3.savefig('demo convergence - {}.png'.format(trial))

        plt.show()

    return best_split


# In[5]:


def get_splits(x, y, splits=None, record_len=None, k=1, max_k=1, debug=False, trial='Demo'):
    if splits is None:
        splits = []
    if debug:
        print('k:', k)
        print('splits:', splits)

    end_buffer = 2 ** (max_k - k) / record_len
    min_split = min(x) + end_buffer + 0.001
    max_split = max(x) - end_buffer - 0.001
    kwargs = dict(min_split=min_split, max_split=max_split, debug=False, trial=trial)
    split = get_split(x, y, **kwargs)
    if split is None:
        get_split(x, y, debug=True, trial=trial)  # this will produce graphs
        return splits
    if split not in splits:
        splits.append(split)
    if k == max_k:
        if debug:
            print('returning:', splits)
        return splits
    else:
        idx = len([_x for _x in x if _x <= split])
        x1, x2 = x[:idx], x[idx:]
        y1, y2 = y[:idx], y[idx:]
        #         print('getting first split with', y1)
        splits = get_splits(x1, y1, record_len=record_len, splits=splits, k=k + 1, max_k=max_k, debug=debug,
                            trial='K{}P1'.format(k + 1))
        #         print('getting second split')
        splits = get_splits(x2, y2, record_len=record_len, splits=splits, k=k + 1, max_k=max_k, debug=debug,
                            trial='K{}P2'.format(k + 1))
        return splits


# ## Main processing script

# In[6]:


period = 'future'
# period = 'historical'

# In[7]:


# read data
if period == 'historical':
    data = pd.read_csv('input/historical-2009.csv', index_col=[0])
    data.index = pd.date_range(start='2009-01-01', periods=len(data), freq='H')
else:
    data = pd.read_csv('input/Price - After ES.csv', index_col=[0], header=0, skiprows=[1])
# data.head()

# In[8]:


# step = 'daily'
step = 'monthly'

if step == 'daily':
    MAX_K = 2
else:
    MAX_K = 3

data_year = 2009  # default for historical; gets overwritten below

if period == 'historical':
    py = 'PY2009'
    # years = range(2000, 2016)
    years = [2009]
else:
    py = 'PY2030-PY2060'
    #     years = range(2030, 2031)
    # years = range(2030, 2061)
    years = [2030, 2045, 2060]  # faster for reading in Pywr model

months = range(1, 13)

blocks_dfs = []
prices_dfs = []
index_dates = []

for year in years:
    m1 = months[0]
    m2 = months[-1]
    start = dt.date(year, m1, 1)
    end = dt.date(year, m2, days_in_month(year, m2))
    if step == 'monthly':
        freq = 'MS'
    else:
        freq = 'D'
    dates = pd.date_range(start=start, end=end, freq=freq)

    if period == 'historical':
        s = data[(data.index.year == 2009)]
    else:
        s = data[str(year)]
        s.index = pd.date_range(start=start, periods=len(s), freq='H')

    print('Year: ', year)

    year_blocks = []
    year_prices = []
    year_dates = []

    for date in dates:

        try:
            index_dates.append(date)
            year_dates.append(date)

            if period == 'future':
                data_year = date.year

            # subset the data
            if step == 'monthly':
                _s = s[s.index.month == date.month]
            else:  # note parentheses are important here
                if isleap(year) and date.month == 12 and date.day == 31:
                    data_day = 30
                else:
                    data_day = date.day
                _s = s[(s.index.year == data_year) & (s.index.month == date.month) & (s.index.day == data_day)]

            y0 = np.array(sorted(_s.values, reverse=True))
            x = np.arange(1, len(y0) + 1)
            x0 = x / max(x)

            record_len = len(x0)  # TODO: make sure this is correct
            splits = get_splits(x0, y0, record_len=record_len, debug=False, max_k=MAX_K, trial='K1')
            splits = sorted(splits)

            split_indices = []
            for split in splits:
                split_indices.append(len([_x for _x in x0 if _x <= split]))
            _blocks = []
            _prices = []
            all_indices = split_indices + [len(x0)]
            for j, idx in enumerate(all_indices):
                a = split_indices[j - 1] if j else 0
                _x = x0[a:idx]
                try:
                    if j == 0:
                        block = max(_x)
                    else:
                        block = max(_x) - x0[last_idx - 1]
                except Exception as err:
                    raise
                last_idx = idx
                price = y0[a:idx].mean()
                _blocks.append(block)
                _prices.append(price)

            year_blocks.append(_blocks)
            year_prices.append(_prices)
        except:
            print('Failed on: ', date)
            continue

    _blocks_df = pd.DataFrame(data=year_blocks, index=year_dates, columns=range(1, len(_blocks) + 1))
    _blocks_df.index.name = 'Date'
    _blocks_df.to_csv('../../data/common/energy prices/piecewise_blocks_{}_PY{}.csv'.format(step, year))
    _prices_df = pd.DataFrame(data=year_prices, index=year_dates, columns=range(1, len(_blocks) + 1))
    _prices_df.index.name = 'Date'
    _prices_df.to_csv('../../data/common/energy prices/piecewise_prices_DpMWh_{}_PY{}.csv'.format(step, year))

    blocks_dfs.append(_blocks_df)
    prices_dfs.append(_prices_df)

# index
# date_index = pd.DatetimeIndex(index_dates)

# blocks
df_blocks = pd.concat(blocks_dfs, axis=0)
df_blocks.to_csv('output/piecewise_blocks_{}_{}.csv'.format(step, py))

# prices
df_prices = pd.concat(prices_dfs, axis=0)
df_prices.to_csv('output/piecewise_prices_DpMWh_{}_{}.csv'.format(step, py))

print('{} {} done!'.format(period, step))

df_blocks.tail()

# In[ ]:
