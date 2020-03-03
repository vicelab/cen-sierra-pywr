#!/usr/bin/env python
# coding: utf-8

# Note: This is derived from https://realpython.com/linear-regression-in-python/

# In[150]:


get_ipython().run_line_magic('matplotlib', 'inline')

import csv
import datetime as dt
from calendar import monthrange, isleap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def days_in_month(year, month):
    return monthrange(year, month)[1]


# In[2]:


def rnd(x, n):
    return round(x*pow(10,n)) / pow(10,n)


# In[3]:


def ss(x, y):
    return np.sum((x - y)**2)


# ## Main processing

# ### Key functions
# 
# `get_split`: This is a basic function that splits a series of x-y pairs into two. It finds the split between an initial lower bound and upper bound (x_min and x_max, respectively) by finding the two contiguous subsets of y that minimize the squared difference between the sum of squares associated with the two sets.
# 
# `get_splits`: This function uses `get_split` to recursively subsplit a series. It currently can only divide by two. I.e., there must be either 1, 2, 4, 8, etc. total number of pieces as a result of the split. This is defined by `max_k` (as in 2^k), which is the square of two associated with the desired total number of pieces.

# In[7]:


def get_split(x, y, debug=False, trial='Demo'):
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
        
        if len(y1) < 2 or len(y2) < 2:
#             search_complete = True
#             return best_split
            print(split)
        
        p1 = np.full(l1, y1.mean())
        p2 = np.full(l2, y2.mean())
        
        ss1 = ss(y1, p1)
        ss2 = ss(y2, p2)

        obj = (ss1 - ss2)**2
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
            if ss1 < ss2: # look higher
                lb = split
                split += (ub - split) / 2
            else: # look lower
                ub = split
                split -= (split - lb) / 2

        objs.append(rel_diff)
        stats.append((rnd(ss1, 3), rnd(ss2, 3)))
        predictions.append(((x1, p1), (x2, p2)))
        
    if debug:
        n = len(predictions)
        
        if debug:
            fig1, axes = plt.subplots(n, 1, figsize=(8, 3*n))
            for i, predictionset in enumerate(predictions):
                ax = axes[i]
                ax.plot(x, y, label='Original prices')
                for j, (xp, yp) in enumerate(predictionset):
                    ax.plot(xp, yp, label='Piece {}, SS={}'.format(j+1, stats[i][j]))
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
            ax.plot(xp, yp, label='Piece {}, SS={}'.format(j+1, stats[-1][j]))
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


# In[8]:


def get_splits(x, y, splits=None, k=1, max_k=1, debug=False, trial='Demo'):
#     print('SPLITS', splits)
    if splits is None:
        splits = []
    if debug:
        print('k:', k)
        print('splits:', splits)
    split = get_split(x, y, debug=False, trial=trial)
    if split is None:
        get_split(x, y, debug=True, trial=trial) # this will produce graphs
        return splits
    if debug:
        print('idx:', idx)
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
        splits = get_splits(x1, y1, splits=splits, k=k+1, max_k=max_k, debug=debug, trial='K{}P1'.format(k+1))
#         print('getting second split')
        splits = get_splits(x2, y2, splits=splits, k=k+1, max_k=max_k, debug=debug, trial='K{}P2'.format(k+1))
        return splits


# ## Main processing script

# In[183]:


period = 'future'
# period = 'historical'


# In[184]:


# read data
if period == 'historical':
    data = pd.read_csv('historical-2009.csv', index_col=[0])
    data.index = pd.date_range(start='2009-01-01', periods=len(hist), freq='H')
else:
    data = pd.read_excel('NetLoad_for_UCM_2030_2060.xlsx', sheet_name='Price - After ES', index_col=[0], header=0, skiprows=[1])
data.head()


# In[185]:


step = 'daily'

if step == 'daily':
    MAX_K = 2
else:
    MAX_K = 3
    
data_year = 2009 # default for historical; gets overwritten below
    
if period == 'historical':
    years = range(2000, 2016)
else:
    # years = range(2030, 2031)
    years = [2030, 2045, 2060]
    
months = range(1,3)

blocks = []
prices = []
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
        s = data[(hist.index.year==2009)]
    else:
        s = data[year]
        s.index = pd.date_range(start=start, periods=len(s), freq='D')
    
    for date in dates:
        index_dates.append(date)
        
        if period == 'future':
            data_year = date.year
        
        # subset the data
        if step == 'monthly':
            _s = s[s.index.month==date.month]
        else: # note parentheses are important here
            if date.month == 2 and date.day == 29:
                data_day = 28
            else:
                data_day = date.day
            _s = s[(s.index.year == data_year) & (s.index.month == date.month) & (s.index.day == data_day)]
        
        y0 = np.array(sorted(_s.values, reverse=True))
        x = np.arange(1, len(y0)+1)
        x0 = x * 100 / x.max()

        splits = get_splits(x0, y0, debug=False, max_k=MAX_K, trial='K1')
        splits = sorted(splits)

        split_indices = []
        for split in splits:
            split_indices.append(len([_x for _x in x0 if _x <= split]))
        _blocks = []
        _prices = []
        all_indices = split_indices + [len(x0)]
        for j, idx in enumerate(all_indices):
            a = split_indices[j-1] if j else 0
            _x = x0[a:idx]
            if j == 0:
                block = max(_x)
            else:
                block = max(_x) - x0[last_idx-1]
            last_idx = idx
            price = y0[a:idx].mean()
            _blocks.append(block)
            _prices.append(price)

        blocks.append(_blocks)
        prices.append(_prices)

# index
# date_index = pd.DatetimeIndex(index_dates)

# blocks
df_blocks = pd.DataFrame(data=blocks, index=index_dates, columns=range(1, len(_blocks)+1))
df_blocks.index.name = 'Date'
df_blocks.to_csv('piecewise_blocks_{}_{}.csv'.format(step, period))

# prices
df_prices = pd.DataFrame(data=prices, index=index_dates, columns=range(1, len(_blocks)+1))
df_prices.index.name = 'Date'
df_prices.to_csv('piecewise_prices_DpMWh_{}_{}.csv'.format(step, period))

print('{} {} done!'.format(period, step))

df_blocks.head()


# In[ ]:




