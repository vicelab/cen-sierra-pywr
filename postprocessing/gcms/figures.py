import os
from itertools import product
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SCENARIOS = 'GCMs test'

data_dir = os.environ['SIERRA_DATA_PATH']
results_dir = os.path.join(data_dir, 'results')
scenarios_dir = os.path.join(results_dir, SCENARIOS)
figs_path = os.path.join(results_dir, 'figures', SCENARIOS)
if not os.path.exists(figs_path):
    os.makedirs(figs_path)

basin_dir_tpl = os.path.join(scenarios_dir, '{basin}/{climate}')

basins = list(d for d in os.listdir(scenarios_dir))
scenarios = list(d for d in os.listdir(os.path.join(scenarios_dir, 'merced')))

basin_scenarios = list(product(basins, scenarios))

# Reservoir storage
RIM_RESERVOIRS = ['New Melones Lake', 'Don Pedro Reservoir', 'Lake McClure', 'Millerton Lake']
WATER_BANK = 'Don Pedro Water Bank'


def create_basic_charts(variable, figname=None):
    df = pd.DataFrame()
    for basin in basins:
        scenario_dfs = []
        print('Processing {}'.format(basin))
        for scenario in scenarios:
            scenario_dir = os.path.join(scenarios_dir, basin, scenario)
            variable_path = os.path.join(scenario_dir, variable + '.csv')

            _df = pd.read_csv(variable_path, header=0, index_col=0, skiprows=[1, 2], parse_dates=True)
            _df.index.name = 'date'
            _df['scenario'] = scenario
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
    figpath = os.path.join(figs_path, figname + '.png')
    fig.savefig(figpath, dpi=300)

    return


create_basic_charts('Reservoir_Storage_mcm')
# create_basic_charts('Hydropower_Flow_mcm')
