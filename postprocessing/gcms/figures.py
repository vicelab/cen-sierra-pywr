import os
from os.path import join, exists
import json
from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CLIMATES = 'GCMs test'

data_dir = os.environ['SIERRA_DATA_PATH']
results_dir = join(data_dir, 'results')
climates_dir = join(results_dir, CLIMATES)
figs_path = join(results_dir, 'figures', CLIMATES)
if not exists(figs_path):
    os.makedirs(figs_path)

basin_dir_tpl = join(climates_dir, '{basin}/{climate}')

basins = list(d for d in os.listdir(climates_dir))

gcms = ['CanESM2', 'CNRM-CM5', 'HadGEM2-ES', 'MIROC5']
gcm_rcps = ['gcms/{}_rcp85'.format(gcm) for gcm in gcms]
climates = ['historical/Livneh'] + gcm_rcps

basin_climates = list(product(basins, climates))

# Reservoir storage
RIM_RESERVOIRS = ['New Melones Lake', 'Don Pedro Reservoir', 'Lake McClure', 'Millerton Lake']
WATER_BANK = 'Don Pedro Water Bank'

# SKIP_ROWS = [1, 2]
SKIP_ROWS = []

MONTHS = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']


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


def get_water_years(dates):
    return [d.year if d.month < 10 else d.year + 1 for d in dates]


def get_water_months(dates):
    return [d.month + 3 if d.month < 10 else d.month - 9 for d in dates]


NODES = {
    'McSwain PH': {
        'head': 16.46,
        'turbine_capacity': 76.45
    },
    'Merced Falls PH': {
        'head': 7.92,
        'turbine_capacity': 49.55
    },
    'New Exchequer PH': {
        'head': 'Lake McClure',
        'turbine_capacity': 8.12
    },
    'Don Pedro PH': {
        'head': 'Don Pedro Reservoir'
    }
}


def create_basic_charts(variable, figname=None):
    df = pd.DataFrame()
    for basin in basins:
        climate_dfs = []
        print('Processing {}'.format(basin))
        for climate in climates:
            climate_dir = join(climates_dir, basin, climate)

            if variable == 'Hydropower_Generation_MWh':
                variable_path = join(climate_dir, 'Hydropower_Flow_mcm.csv')
            else:
                variable_path = join(climate_dir, variable + '.csv')

            _df = read_csv(variable_path)
            _df.index.name = 'date'

            if variable == 'Hydropower_Generation_MWh':

                # Calculate energy in MWh from energy equation:
                # P = rho * g * Q * h * eta
                # P = power (Joules?)
                # rho = density (1000 kg/m^3); assume constant
                # g = gravitational constant (9.81 m/s^2); assume constant
                # Q = flowrate (m^3/s); variable
                # h = head (m); could be fixed or variable
                # eta = efficiency (assume 0.85 for now)

                # E = P * 24 / 1e6 (double check) - convert from Joules/second to MWh (per day)

                # load model
                model_path = '../../{}/pywr_model.json'.format(basin)
                with open(model_path) as f:
                    model = json.load(f)

                # get elevations
                elev_path = join(climate_dir, 'Reservoir_Elevation_m.csv')
                if os.path.exists(elev_path):
                    elev = read_csv(elev_path)
                else:
                    elev = None

                keepers = []
                eta = 0.85
                gamma = 9810  # = rho * g = 1000 * 9.81
                nodes = {n['name']: n for n in model['nodes']}
                for ph in _df:
                    node = nodes[ph]
                    Q = _df[ph] / 0.0864  # convert to mcm
                    h = node.get('head', NODES.get(ph, {}).get('head'))  # m
                    if type(h) == str and elev is not None:
                        h = elev.get(h)
                    elif type(h) not in [int, float]:
                        h = None
                    if h is None:
                        continue
                    keepers.append(ph)
                    Qmax = node.get('turbine_capacity')  # cms
                    if type(Qmax) not in [int, float]:
                        Qmax = NODES.get(ph, {}).get('turbine_capacity', 0)
                    Q = Q.map(lambda q: min(q, Qmax))
                    MWh = eta * gamma * Q * h * 24 / 1e6
                    _df[ph] = MWh

                _df = _df[keepers]

            _df['climate'] = climate
            _df.reset_index(inplace=True)
            _df.set_index(['date', 'climate'], inplace=True)
            climate_dfs.append(_df)
        basin_df = pd.concat(climate_dfs, axis=1).sum(axis=1).to_frame()
        basin_df['basin'] = basin
        basin_df = basin_df.reset_index().set_index(['climate', 'basin', 'date'])
        basin_df.columns = [variable]
        df = df.append(basin_df)


    ylabel_parts = variable.split('_')
    ylabel = ' '.join(ylabel_parts[:2] + ['({})'.format(ylabel_parts[-1])])
    if 'MWh' in ylabel:
        ylabel = ylabel.replace('MWh', 'GWh')

    # monthly box plots
    df_monthly = df.copy()
    # df_monthly['WM'] = get_water_months(df_monthly.reset_index()['date'])
    level_values = df_monthly.index.get_level_values
    groups = [pd.Grouper(level='climate'), pd.Grouper(level='basin'), pd.Grouper(level='date', freq='MS')]
    df_monthly = df_monthly.groupby(groups).sum() / 1e3
    df_monthly['WM'] = get_water_months(df_monthly.reset_index()['date'])
    df_monthly = df_monthly.reindex(level='climate', index=climates)
    df_monthly.reset_index(inplace=True)
    N = len(basins)
    fig1, axes = plt.subplots(N, figsize=(10, 4*N))
    for i, basin in enumerate(basins):
        ax = axes[i]
        data = df_monthly[df_monthly['basin']==basin]
        sns.boxplot(data=data, x='WM', y=variable, hue='climate', ax=ax)
        ax.set_title(basin)
        ax.set_ylabel(ylabel)
        ax.legend(loc='lower right')
        ax.set_xticklabels(MONTHS)
        ax.set_xlabel('Month', size=12)

    plt.show()
    if not figname:
        figname = variable
    figpath = join(figs_path, figname + '_monthly.png')
    fig1.savefig(figpath, dpi=600)

    # annual box plots by basin
    df_annual = df.copy()
    df_annual['WY'] = get_water_years(df_annual.reset_index()['date'])
    df_annual = df_annual.reset_index().groupby(['basin', 'climate', 'WY']).sum() / 1000
    df_annual = df_annual.reindex(level='climate', index=climates)
    df_annual.reset_index(inplace=True)
    fig2, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df_annual, x='basin', y=variable, hue='climate', ax=ax)
    ax.set_ylabel(ylabel)
    plt.show()
    if not figname:
        figname = variable
    figpath = join(figs_path, figname + '_annual.png')
    fig2.savefig(figpath, dpi=600)

    return


def create_spill_charts():
    spill_df = pd.DataFrame()
    for climate in climates:
        for basin in basins:
            climate_dir = join(climates_dir, basin, climate)

            var = 'InstreamFlowRequirement_{var}_mcm.csv'
            flow_path = join(climate_dir, var.format(var='Flow'))
            min_flow_path = join(climate_dir, var.format(var='Min Flow'))

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
    fig, axes = plt.subplots(N, 1, figsize=(8, 3 * N))
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
    create_basic_charts('Hydropower_Generation_MWh')

    # create_spill_charts()
