import os
import datetime as dt
from datetime import date
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
import seaborn as sns

file_suffix = date.today().strftime('%Y-%m-%d')
suffix = ' - {}'.format(file_suffix) if file_suffix else ''
data_path = os.environ['SIERRA_DATA_PATH']
output_dir = os.environ['SIERRA_RESULTS_PATH']

#Figures 11 and 12

result_dir = './results' 
basin = 'stanislaus'
hydrology_scenario = 'historical/Livneh'

year = 1990
n = 3
start = dt.datetime(year, 10, 1)
end = dt.datetime(year+n, 9, 30)
start_months = [
    (dt.datetime(year, 10, 1), dt.datetime(year+1, 2, 1)),
    (dt.datetime(year+1, 1, 1), dt.datetime(year+1, 5, 1))
]

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

ph_reservoirs = {
    'Donnells PH': ['Donnells Reservoir'],
    'Stanislaus PH': ['Relief Reservoir', 'Donnells Reservoir', 'Beardsley Reservoir', 'Pinecrest Reservoir']
}

# ph = 'Stanislaus PH'
ph = 'Donnells PH'
facility_groups = [ph_reservoirs[ph], [ph]]

max_flow = {
    'Donnells PH': 700 / 35.31 * 0.0864,
    'Stanislaus PH': 1.3,
    'Beardsley PH': 700 / 35.31 * 0.0864,
    'Sand Bar PH': 1.5
}

ylabels = {
    'storage': r'Storage ($million\/m^3$)',
#     'flow': r'Flow ($\%\/of\/capacity$)'
    'flow': r'Flow ($million\/m^3/day$)'
}

subplot_letters = [['a', 'b'], ['c', 'd']]

sns.set_style('whitegrid')

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"]})

fontsize=12

def get_planning_df():
    run_name = 'planning method'
    basin_path = os.path.join(result_dir, run_name, basin, r'historical\Livneh')
    file_path = os.path.join(basin_path, 'planning_model_results.csv')
    df = pd.read_csv(file_path, index_col=[0, 1], parse_dates=True, header=[0], skiprows=[1,2])
    df.index.names = ['month', 'planning month']
    return df

# # Planning example

def plot_optimal(N=3):

    sns.set_palette('Set1')
    
    df = get_planning_df()

    months = df.index.levels[0]
    fig, axes = plt.subplots(2,2,figsize=(12,5))

    for i, param in enumerate(['storage', 'flow']):
        facilities = facility_groups[i]
        for j, (start_month, end_month) in enumerate(start_months):
            ax = axes[i,j]
            start_month_str = start_month.strftime('%b, %Y')
            start_dates = pd.date_range(start_month, end_month, freq='M')
            for m, start_date in enumerate(start_dates):
                start_date_str = start_date.strftime('%Y-%m-01')
                cols = ['{}/{}'.format(f, param) for f in facilities]
                _df = df[cols].loc[(start_date_str,)].sum(axis=1)
                x = _df.index.get_level_values(0)
                y = _df.values

                if param == 'flow':
                    y = [_y / 30 for k, _y in enumerate(y)]
    #                 y = [_y / (max_flow[ph] * days_in_month[x[k].month-1]) * 100 for k, _y in enumerate(y)]
    #                 y = [_y / (max_flow[ph] * 30) * 100 for k, _y in enumerate(y)]
    #                 y = [_y / max_flow[facilities[0]] * 100 for k, _y in enumerate(y)]

                ax.plot(x, y, marker='os^v'[m], label=start_date.strftime('%Y-%m-01'))

            if (i, j) in [(0,0), (0,1)]:
                ax.legend(title='Start date', fontsize=fontsize)

            if len(facilities) > 1:
                facility_name = 'Aggregated {}'.format(param)
            else:
                facility_name = facilities[0].replace('PH', 'Powerhouse')

            subplot_title = '{}) {} ({})'.format(subplot_letters[i][j], facility_name, start_month_str)
            ax.set_title(subplot_title, fontsize=fontsize+1)
            ax.set_ylabel(ylabels[param], fontsize=fontsize)
            if param == 'storage':
                ax.set_ylim(bottom=0)
            else:
    #             ax.set_ylim(0, 105)
                ax.set_ylim(bottom=0)
            ax.set_xlabel('Planning month', fontsize=fontsize)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig('figure - planning model demo.png', bbox_inches='tight', dpi=600)
plot_optimal()

# # Planning vs. scheduled - daily

def plot_simulated(resolution='daily'):
    # sns.set_palette(['grey', 'blue', 'green'])
    sns.set_palette('bright')

    fig, axes = plt.subplots(2,1,figsize=(12,6))
    
    df_planning = get_planning_df()

    planning_dates = pd.date_range(start=start, end=end, freq='M')
    scheduling_dates = pd.date_range(start=start, end=end)
    
    for i, var in enumerate(['storage', 'flow']):
        data_path = os.environ['SIERRA_DATA_PATH']
        # observed flows
        path = Path(data_path, 'Stanislaus River/gauges/streamflow_cfs.csv')
        gauges = {
            'Stanislaus PH': 'USGS 11295505 STANISLAUS PP NR HATHAWAY PINES CA',
            'Donnells PH': 'USGS 11292610 DONNELL PH NR STRAWBERRY CA',
            'Beardsley PH': 'USGS 11292820 BEARDSLEY PH NR STRAWBERRY CA'
        }
        
        # if ph in gauges:
        if var == 'flow':
            df_obs = pd.read_csv(path, index_col=0, parse_dates=True)[[gauges[ph]]].loc[start:end] / 35.315 * 0.0864
            df_obs.columns = ['Flow']
            df_obs['Source'] = 'Observed'
        else:
            df_obs = pd.DataFrame()

        # planning results
        x_pl = [dt.datetime(d.year, d.month, 1) for d in planning_dates]
        facilities = facility_groups[i]
        cols = ['{}/{}'.format(f, var) for f in facilities]
        y_pl = [df_planning[cols].sum(axis=1).loc[(d, d)] / 30 for d in planning_dates.strftime('%Y-%m-01')]
        df_pl = pd.DataFrame(index=pd.DatetimeIndex(x_pl), data=y_pl, columns=[var]) * (30 if var == 'storage' else 1)
        df_pl.index.name = 'Date'
        df_pl = df_pl.resample('D').ffill()
        df_pl['Source'] = 'Planned'

        # scheduling results
        def read_results(scenario, source):
            run_nome = scenario
            var_filename = 'Hydropower_Flow_mcm.csv' if var == 'flow' else 'Reservoir_Storage_mcm.csv'
            file_path = os.path.join(result_dir, run_nome, basin, hydrology_scenario, var_filename)
            _df = pd.read_csv(file_path, index_col=0, parse_dates=True, header=0)[facilities].sum(axis=1).to_frame()
            _df.columns = [var]
            if resolution == 'monthly':
                _df = _df.resample('MS').mean()
#                 _df.index = pd.DatetimeIndex([d.strftime('%Y-%m-01') for d in _df.index])
                _df = _df.resample('D').ffill()
                _df.index.name = 'Date'
            _df['Source'] = source
            return _df
        
        # optimized results
        df_sch = read_results('planning method', 'Scheduled w/ planning')
        
        # non-optimized results
        run_names = 'no planning method' 
       # basin_path = os.path.join(results_path, run_name, basin, r'historical\Livneh')
        df_np = read_results(run_names, 'Scheduled w/o planning')

        df_plt = pd.concat([df_pl, df_np, df_sch], axis=0)
        df_plt = df_plt.reset_index()
        df_plt = df_plt[df_plt['Date'].isin(df_pl.index)]        
        
        ax = axes[i]
        markers = None if resolution == 'daily' else 'ooo'
        sns.lineplot(data=df_plt, x='Date', y=var, style='Source', hue='Source', ax=ax)
        ax.set_ylabel(ylabels[var])
        ax.set_xlabel('')
        if i==0:
            ax.legend(title='', loc='lower right')
        else:
            ax.legend().remove()
    fig.autofmt_xdate()
    fig.savefig(f'figure - comparisons - {resolution}.png', dpi=600, bbox_inches='tight')
    plt.show()
print(ph)
plot_simulated('daily')
plot_simulated('monthly')


#Figure 13

sns.set_style('whitegrid')
sns.set_palette('Set1')

basin = 'stanislaus'
node = 'IFR bl Beardsley Afterbay'
climate_scenario = 'historical/Livneh'

fig, ax = plt.subplots(1, 1, figsize=(12, 4))

start = '1992-10-01'
end = '1994-09-03'

obs_path = Path(data_path, 'Stanislaus River/gauges/streamflow_cfs.csv')
df_obs = pd.read_csv(obs_path, index_col=0, parse_dates=True)
df_obs = df_obs['USGS 11292900 MF STANISLAUS R BL BEARDSLEY DAM CA'][start:end] / 35.315


def get_df(scenario, var, label=None):
    csv_path = Path(output_dir, scenario + suffix, basin, climate_scenario)
    path = Path(csv_path, f'InstreamFlowRequirement_{var}_mcm.csv')
    _df = pd.read_csv(path, index_col=0, parse_dates=True, header=0)[node][start:end].to_frame()
    _df = _df * 1e6 / 24 / 60 / 60
    _df.index.name = 'Date'
    _df['Variable'] = label or var
    return _df


scen = 'planning'
df_flow = get_df(scen, 'Flow')
df_min = get_df(scen, 'Min Flow')
df_range = get_df(scen, 'Max Flow')
df_max = df_min + df_range
df_max['Variable'] = 'Max Flow'

df_flow_no_rr = get_df('planning - no rr', 'Flow', label='No RR')

ax.plot(df_min.index, df_min[node].values, color='red', linewidth=4, alpha=0.75, linestyle='--',
        label='Min. flow req\'t w/ ramping limit')
ax.plot(df_obs.index, df_obs.values, color='black', linewidth=3.5, alpha=0.75, label='Observed flow')
ax.plot(df_flow.index, df_flow_no_rr[node].values, color='orange', label='Sim. flow w/o ramping limit')
# ax.fill_between(df_min.index, df_min[node].values, df_max[node].values, alpha=0.2, label='Maximum flow (range)')
ax.plot(df_flow.index, df_flow[node].values, color='green', label='Sim. flow w/ ramping limit')
ax.set_yscale('log')
# ax.set_ylim(bottom=0, top=3)
ax.set_ylabel(r'Flow (m$^3$/s) [log scale]', fontsize=11)
ax.legend(loc='upper right', fontsize=11)

fig.savefig('figure - flow below Beardsley Afterbay.png', dpi=600, bbox_inches='tight')

plt.show()

# In[ ]:


#Figure 14

input_dir = os.environ['SIERRA_DATA_PATH']

output_dir = os.environ['SIERRA_RESULTS_PATH']

file_suffix = date.today().strftime('%Y-%m-%d')
suffix = ' - {}'.format(file_suffix) if file_suffix else ''

# prices
prices_path = Path(input_dir, r'common\energy prices\prices_pivoted_select_years.csv')
s = pd.read_csv(prices_path, index_col=0, header=0, parse_dates=True).mean(axis=1)
s = s[s.index.year == 2009]
s_oct_dec = s[s.index.month >= 10].values
s_jan_sep = s[s.index.month <= 9].values
idx_oct_dec = [date(d.year - 1, d.month, d.day) for d in s.index if d.month >= 10]
idx_jan_sep = [date(d.year, d.month, d.day) for d in s.index if d.month <= 9]
dates = idx_oct_dec + idx_jan_sep

prices = pd.Series(
    index=dates,
    data=np.concatenate((s_oct_dec, s_jan_sep))
)


def read_csv(path):
    start = '2004-10-01'
    end = '2005-09-30'
    df = pd.read_csv(path, index_col=0, header=0, parse_dates=True)[start:end]
    return df


# full natural flow
fnf_path = Path(input_dir, r'Upper San Joaquin River\hydrology\historical\Livneh\preprocessed',
                'full_natural_flow_daily_mcm.csv')
fnf = read_csv(fnf_path)


def get_energy_df(study):
    path = Path(output_dir, study, 'upper_san_joaquin/historical/Livneh', 'Hydropower_Energy_MWh.csv')
    df = read_csv(path)
    df = df.sum(axis=1) / 1000
    return df


# hydropower
hp_no_planning = get_energy_df('no planning' + suffix)
hp_planning = get_energy_df('planning' + suffix)

# prices.index = hp_planning.index

# figure
fig, axes = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(9, 5))

# top
ax0 = axes[0]
ax0.plot(prices, color='black')
ax0.set_ylabel('Price ($/MWh)')
ax0.xaxis.set_major_formatter(DateFormatter('%b'))
ax0.set_xlim(prices.index[0], prices.index[-1])

# bottom
ax1 = axes[1]
ax1.plot(hp_no_planning, color='orange', label='Energy w/o planning')
ax1.plot(hp_planning, color='green', label='Energy w/ planning')
ax1.set_ylim(0, 60)
ax1.set_ylabel('Energy (GWh/day)')

ax2 = ax1.twinx()
ax2.plot(fnf, color='blue', label='Full natural flow')
ax2.set_ylim(0, 60)
ax2.set_ylabel('Flow (million m$^3$/day)')
ax2.set_xlim(fnf.index[0], fnf.index[-1])

for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(DateFormatter('%b'))

fig.tight_layout()
fig.legend(loc='lower center', ncol=3, frameon=False, borderaxespad=.2)
plt.subplots_adjust(bottom=0.12)

fig.savefig('figure 14 - usj energy.png', dpi=600)

#Figure 15

local_obs_dir = './data/observed'

no_opt_path = Path(output_dir, 'no planning' + suffix)
opt_path = Path(output_dir, 'planning' + suffix)
scenario_names = ['observed', 'w/o planning', 'w/ planning']

facilities_path = Path(local_obs_dir, 'runoff/Upper San Joaquin River/ObservedData_USJ.csv')
facilities_list = pd.read_csv(facilities_path, dtype=str)
modeled_names = [str(s) for s in facilities_list['Name (Model)']]
observed_names = [str(s) for s in facilities_list['Name (Observed)']]

# storage data
scenarios = ['observed', 'no planning', 'planning']
dfs = []
for i, scenario in enumerate(scenarios):
    run_name = scenario + suffix
    if scenario == 'observed':
        fp = Path(local_obs_dir, r'energy\monthly_hydro_1980_2018_MWh.csv')
        df = pd.read_csv(fp, index_col=0, header=0, parse_dates=True).dropna(axis=1)
        df = df[[c for c in df if c in observed_names]]
    else:
        fp = Path(output_dir, run_name, 'upper_san_joaquin/historical/Livneh/Hydropower_Energy_MWh.csv')
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

# storage data
dfs = []
for i, scenario in enumerate(scenarios):
    if scenario == 'observed':
        fp = Path(input_dir, r'Upper San Joaquin River\gauges\storage_mcm.csv')
    else:
        fp = Path(output_dir, run_name, 'upper_san_joaquin/historical/Livneh/Reservoir_Storage_mcm.csv')
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

# plot data
fig, axes = plt.subplots(2, 1, figsize=(9, 5))

ylabel_energy = 'Energy (GWh)'
ylabel_storage = 'Storage (million m$^3$)'
month_labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

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
fig.savefig('figure 15 - usj aggregated energy and storage.png', dpi=600)
