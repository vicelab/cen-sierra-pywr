import os
from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.timeseries as snsts


def read_csv(path):
    return pd.read_csv(path, index_col=0, header=0, parse_dates=True)


SCENARIOS = 'GCMs test'

MONTHS = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

data_dir = os.environ['SIERRA_DATA_PATH']
results_dir = os.path.join(data_dir, 'results')
scenarios_dir = os.path.join(results_dir, SCENARIOS)
figs_path = os.path.join(results_dir, 'figures', SCENARIOS)
if not os.path.exists(figs_path):
    os.makedirs(figs_path)

basin_dir_tpl = os.path.join(scenarios_dir, '{basin}/{climate}')

basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

climates = ['gcms/{}'.format(d) for d in os.listdir(os.path.join(data_dir, 'Merced River/hydrology/gcms')) if
            'rcp85' in d]


# BOX PLOTS

def create_box_plots():
    # https://seaborn.pydata.org/generated/seaborn.boxplot.html
    df = pd.DataFrame()
    climates.insert(0, 'historical/Livneh')
    for climate in climates:
        for basin in basins:
            basin_name = basin.replace('_', ' ').title() + ' River'
            scenario_dir = os.path.join(data_dir, basin_name, 'hydrology', climate)
            fnf_path = os.path.join(scenario_dir, 'preprocessed', 'full_natural_flow_annual_mcm.csv')
            _df = pd.read_csv(fnf_path, index_col=0, header=0)

            if 'gcms' in climate:
                _df = _df.loc[range(2030, 2061)]

            _df['climate'] = climate
            _df['basin'] = basin
            _df.reset_index(inplace=True)
            _df = _df.set_index(['basin', 'climate', 'WY']).reset_index()
            df = df.append(_df)

    df['flow'] /= 1233.5  # convert to MAF
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x='basin', y='flow', hue='climate', ax=ax, whis=10)

    ax.set_ylabel('Annual runoff (MAF)', size=12)
    ax.set_xlabel('Basin', size=12)

    plt.show()

    fig_path = os.path.join(figs_path, 'basin_runoff_boxplots.png')

    fig.savefig(fig_path, dpi=600)


def create_monthly_plots():
    df = pd.DataFrame()
    climates.insert(0, 'historical/Livneh')
    for climate in climates:
        basin_df = pd.DataFrame()
        for basin in basins:
            basin_name = basin.replace('_', ' ').title() + ' River'
            scenario_dir = os.path.join(data_dir, basin_name, 'hydrology', climate)
            fnf_path = os.path.join(scenario_dir, 'preprocessed', 'full_natural_flow_monthly_mcm.csv')
            _df = pd.read_csv(fnf_path, index_col=0, header=0, parse_dates=True)
            _df['water month'] = [m + 3 if m < 10 else m - 9 for m in _df.index.month]
            # _df['water year'] = [d.year + 1 if d.month > 9 else d.year for d in _df.index]
            _df['climate'] = climate
            _df['basin'] = basin
            _df.reset_index(inplace=True)
            _df = _df.set_index(['basin', 'climate', 'water month']).reset_index()
            df = df.append(_df)

    # df = df.groupby(['climate', 'water month']).sum().reset_index()
    df['flow'] /= 1233.5  # convert to MAF
    # fig, axes = plt.subplots(5, 1, figsize=(12, 15))
    # for i, climate in enumerate(climates):
    #     ax = axes[i]
    #     # sns.lineplot(data=df[df['climate']==climate], x='water month', y='flow', hue='climate', ax=ax,
    #     #              estimator='mean', ci='sd')
    #     sns.boxplot(data=df[df['climate']==climate], x='water month', y='flow', whis=100, ax=ax)
    #     # snsts._plot_ci_band(ax=ax, data=df, x='water month')
    #
    #     ax.set_ylabel('Runoff (MAF)')
    #     ax.set_xlabel('water month (Oct-Sep)')

    fig, ax = plt.subplots(figsize=(8, 5))
    # sns.lineplot(data=df[df['climate']==climate], x='water month', y='flow', hue='climate', ax=ax,
    #              estimator='mean', ci='sd')
    sns.boxplot(data=df, x='water month', y='flow', hue='climate', whis=100, ax=ax)

    ax.set_ylabel('Monthly runoff (MAF)', size=12)
    ax.set_xticklabels(MONTHS)
    ax.set_xlabel('Month', size=12)

    plt.show()

    fig_path = os.path.join(figs_path, 'basin_runoff_boxplot_monthly.png')
    # fig_path = os.path.join(figs_path, 'basin_runoff_shaded_monthly.png')

    fig.savefig(fig_path, dpi=600)


create_box_plots()
create_monthly_plots()

print('done!')
