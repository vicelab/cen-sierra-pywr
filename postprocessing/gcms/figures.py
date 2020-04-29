import os
from os.path import join, exists
from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SCENARIOS = 'GCMs test'

data_dir = os.environ['SIERRA_DATA_PATH']
results_dir = join(data_dir, 'results')
climates_dir = join(results_dir, SCENARIOS)
figs_path = join(results_dir, 'figures', SCENARIOS)
if not exists(figs_path):
    os.makedirs(figs_path)

basin_dir_tpl = join(climates_dir, '{basin}/{climate}')

basins = list(d for d in os.listdir(climates_dir))

gcms = ['CanESM2', 'CNRM-CM5', 'HadGEM2-ES', 'MIROC5']
gcm_rcps = [gcm + '_rcp85' for gcm in gcms]
climates = ['Livneh'] + gcm_rcps

basin_scenarios = list(product(basins, climates))

# Reservoir storage
RIM_RESERVOIRS = ['New Melones Lake', 'Don Pedro Reservoir', 'Lake McClure', 'Millerton Lake']
WATER_BANK = 'Don Pedro Water Bank'

SKIP_ROWS = [1, 2]


def read_csv(path, index_name='date', **kwargs):
    kwargs['index_col'] = kwargs.pop('index_col', 0)
    kwargs['header'] = kwargs.pop('header', 0)
    kwargs['parse_dates'] = kwargs.pop('parse_dates', True)
    kwargs['skiprows'] = kwargs.pop('skiprows', SKIP_ROWS)
    df = pd.read_csv(path, **kwargs)
    df.index.name = index_name

    return df


def get_common_columns(*args):
    all_cols = []
    for df in args:
        all_cols.extend(df.columns)

    return sorted(list(set(all_cols)))


def get_water_years(index):
    return [d.year if d.month < 10 else d.year + 1 for d in index]


def create_basic_charts(variable, figname=None):
    df = pd.DataFrame()
    for basin in basins:
        scenario_dfs = []
        print('Processing {}'.format(basin))
        for climate in climates:
            scenario_dir = join(climates_dir, basin, climate)
            variable_path = join(scenario_dir, variable + '.csv')

            _df = pd.read_csv(variable_path, header=0, index_col=0, skiprows=[1, 2], parse_dates=True)
            _df.index.name = 'date'
            _df['scenario'] = climate
            _df.reset_index(inplace=True)
            _df.set_index(['date', 'scenario'], inplace=True)
            scenario_dfs.append(_df)
        basin_df = pd.concat(scenario_dfs, axis=1).sum(axis=1).to_frame()
        basin_df['basin'] = basin
        basin_df = basin_df.reset_index().set_index(['date', 'basin', 'scenario'])
        basin_df.columns = [variable]
        df = df.append(basin_df)

    # annual
    # df_annual = df.resample('YS').mean().sum(axis=1)

    df.reset_index(inplace=True)

    # boxplots
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x='basin', y=variable, hue='scenario', ax=ax)

    plt.show()

    if not figname:
        figname = variable
    figpath = join(figs_path, figname + '.png')
    fig.savefig(figpath, dpi=300)

    return


def create_spill_charts():
    spill_df = pd.DataFrame()
    for climate in climates:
        for basin in basins:
            scenario_dir = join(climates_dir, basin, climate)

            var = 'InstreamFlowRequirement_{var}_mcm.csv'
            flow_path = join(scenario_dir, var.format(var='Flow'))
            min_flow_path = join(scenario_dir, var.format(var='Min Flow'))

            flow_df = read_csv(flow_path)

            if not exists(min_flow_path):
                continue
            min_flow_df = read_csv(min_flow_path)

            locs = get_common_columns(flow_df, min_flow_df)

            _df = flow_df[locs] - min_flow_df[locs]
            _df[_df < 0] = 0
            _df['WY'] = get_water_years(_df.index)
            _df.reset_index(inplace=True)
            _df.set_index(['date', 'WY'], inplace=True)
            _df = _df.stack().to_frame()
            _df.index.names = ['date', 'WY', 'location']
            _df.columns = ['value']
            _df['climate'] = climate
            _df['basin'] = basin
            spill_df = spill_df.append(_df)

    df = spill_df.groupby(['climate', 'location', 'WY', 'date']).sum()
    df = df.unstack(level='location')
    df.columns = df.columns.droplevel(level=0)
    df = df.reindex(level='climate', index=climates)

    # plots by facility
    df2 = df.groupby(['climate', 'WY']).sum() / 1233.5
    N = len(df2.columns)
    fig, axes = plt.subplots(N, 1, figsize=(8, 3*N))
    for i, loc in enumerate(df2.columns):
        ax = axes[i]
        data = df2[loc].reset_index()
        sns.boxplot(data=data, x='climate', y=loc, ax=ax)
        ax.set_title(loc)
        ax.set_ylabel('Annual flow (MAF)')
    plt.show()

    # box plots by basin
    df = spill_df.groupby(['climate', 'basin', 'WY']).sum() / 1233.5
    df = df.reindex(level='climate', index=climates)

    fig, ax = plt.subplots(figsize=(8, 5))
    data = df.reset_index()
    sns.boxplot(data=data, ax=ax, x='basin', y='value', hue='climate')
    ax.set_ylabel('Total basin spill (MAF)')

    plt.show()

    return


if __name__ == '__main__':
    # create_basic_charts('Reservoir_Storage_mcm')
    # create_basic_charts('Hydropower_Flow_mcm')

    create_spill_charts()
