#!/usr/bin/env python
# coding: utf-8

# In[1]:


# get_ipython().run_line_magic('matplotlib', 'inline')

import os
import datetime as dt
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


results_dir = '../results'
no_opt_path = Path(results_dir, 'no optimization')
opt_path = Path(results_dir, 'optimization')
scenario_names = ['observed', 'w/o planning', 'w/ planning']


# In[3]:


facilities_list = pd.read_csv('../../data/observed/runoff/Upper San Joaquin River/ObservedData_USJ.csv', dtype=str)
modeled_names = [str(s) for s in facilities_list['Name (Model)']]
observed_names = [str(s) for s in facilities_list['Name (Observed)']]
print(observed_names)
print(modeled_names)


# In[4]:


# Energy data
scenarios = ['observed', 'no optimization', 'optimization']
dfs = []
for i, scenario in enumerate(scenarios):
    if scenario == 'observed':
        fp = r'..\..\data\observed\energy\monthly_hydro_1980_2018_MWh.csv'
        df = pd.read_csv(fp, index_col=0, header=0, parse_dates=True).dropna(axis=1)
        df = df[[c for c in df if c in observed_names]]
    else:
        fp = Path(results_dir, scenario, 'upper_san_joaquin/historical/Livneh/Hydropower_Energy_MWh.csv')
        df = pd.read_csv(fp, index_col=0, header=0, parse_dates=True)
        df = df[[c for c in df if c in modeled_names]]
        
    df = df.loc['1980-10-01':'2012-09-30']
#     print(scenario)
#     print(df.head())
    df = df.sum(axis=1).to_frame()
    df.columns = ['Total']
    df = df.resample('M').sum() / 1e3
    df['scenario'] = scenario_names[i]
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['month'] = [m - 9 if m >= 10 else m + 3 for m in df['month']]
    df = df.reset_index()
    del df['Date']
    df = df.set_index(['scenario', 'year', 'month'])
    dfs.extend([df])
    
df_energy = pd.concat(dfs, axis=0).reset_index()
df_energy.head()


# In[5]:


# Storage data
# read in simulated storage

results_dir = '../results'
no_opt_path = Path(results_dir, 'no optimization')
opt_path = Path(results_dir, 'optimization')

scenarios = ['no optimization', 'optimization']
dfs = []
for i, scenario in enumerate(['observed'] + scenarios):
    if scenario == 'observed':
        fp = Path(r'..\..\data\observed\runoff\Upper San Joaquin River\storage_mcm.csv')
    else:
        fp = Path(results_dir, scenario, 'upper_san_joaquin/historical/Livneh/Reservoir_Storage_mcm.csv')
    df = pd.read_csv(fp, index_col=0, header=0, parse_dates=True)
#     df_millerton = df[[c for c in df if 'millerton' in c.lower()]].sum(axis=1)
    df = df[[c for c in df if 'millerton' not in c.lower()]].sum(axis=1).to_frame()
#     df = pd.concat([df_upper_basin, df_millerton], axis=1)
#     df.columns = ['Millerton Lake', 'Upper Basin']
    df.columns = ['Total']
    df = df.loc['1965-10-01':'2012-09-30']
    df = df.resample('M').mean()
    df['scenario'] = scenario_names[i]
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['month'] = [m - 9 if m >= 10 else m + 3 for m in df['month']]
    df = df.reset_index()
    del df['Date']
    df = df.set_index(['scenario', 'year', 'month'])
    dfs.extend([df])
df_storage = pd.concat(dfs, axis=0).reset_index()
df_storage.head()


# In[14]:


# plot data
fig, axes = plt.subplots(2,1,figsize=(9,5))

ylabel_energy = 'Energy ($GWh$)'
ylabel_storage = 'Storage ($million\ m^3$)'
month_labels = ['Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep']

# Subplot: Energy
ax = axes[0]
sns.boxplot(data=df_energy, x='month', y='Total', hue='scenario', ax=ax)
ax.set_title('a) Energy (WY1980-2012; n=12)')
ax.set_ylabel(ylabel_energy)
ax.set_xlabel('')
ax.set_xticklabels(month_labels)
ax.legend(loc='upper left')

# Subplot: Storage
ax = axes[1]
sns.boxplot(data=df_storage, x='month', y='Total', hue='scenario', ax=ax)
ax.set_title('b) Storage (WY1966-2012; n=6)')
ax.set_ylabel(ylabel_storage)
ax.set_xlabel('')
ax.set_xticklabels(month_labels)
ax.legend(loc='upper left')

fig.tight_layout()
fig.savefig('figure - hydropower and storage.png', dpi=600)
plt.show()


# In[ ]:




