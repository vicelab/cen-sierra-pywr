import os
import pandas as pd
import matplotlib.pyplot as plt

results_dir = "../../results/development"
data_dir = os.environ['SIERRA_DATA_PATH']

figs_path = os.path.join(data_dir, 'results', 'figures', 'performance')
if not os.path.exists(figs_path):
    os.makedirs(figs_path)

reservoirs = ['New Melones Lake', 'Don Pedro Reservoir', 'Lake McClure', 'Millerton Lake']
basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

variables = ['Reservoir_Storage_mcm']

gauge_lookup = pd.read_csv('../../dashapp/gauges.csv', index_col=1, header=0, squeeze=True)
gauge_to_node = gauge_lookup.to_dict()
years = range(1980, 2000+1)
for var in variables:
    dfs = []
    obs_dfs = []
    for basin in basins:
        basin_path = os.path.join(results_dir, basin, 'historical/Livneh')
        variable_path = os.path.join(basin_path, var + '.csv')
        df = pd.read_csv(variable_path, header=0, index_col=0, skiprows=[1, 2], parse_dates=True)
        df.index.name = 'date'
        nodes = [c for c in df.columns if c in reservoirs]
        df = df[nodes]
        dfs.append(df)

        full_basin_name = basin.replace('_', ' ').title() + ' River'
        obs_path = os.path.join(data_dir, full_basin_name, 'gauges', 'storage_mcm.csv')
        obs_df = pd.read_csv(obs_path, index_col=0, header=0, parse_dates=True)
        obs_df.rename(columns=gauge_to_node, inplace=True)
        obs_dfs.append(obs_df[nodes])

    df = pd.concat(dfs, axis=1)
    # df = df[df.index.year in years]
    # min_year = min(df.index.year)
    # max_year = max(df.index.year)
    # years = range(min_year, max_year)
    obs_df = pd.concat(obs_dfs, axis=1)

    # resample and convert to TAF
    obs_df = obs_df.loc[df.index].resample('MS').mean() / 1.2335
    df = df.resample('MS').mean() / 1.2335

    N = len(df.columns)
    fig, axes = plt.subplots(N, 1, figsize=(12, 3*N))
    for i, node in enumerate(df.columns):
        ax = axes[i]

        ax.plot(df.index, df[node], label='Simulated')
        ax.plot(obs_df.index, obs_df[node], label='Observed')

        # general
        ax.set_title(node, size=14)
        ax.set_xlabel('Date')
        ax.set_ylim(0)
        ax.set_ylabel('Storage (TAF)', size=12)
        if i == 0:
            ax.legend(ncol=1, loc='lower right')

    plt.show()

    fig_path = os.path.join(figs_path, 'rim_reservoir_storage.png')
    fig.savefig(fig_path, dpi=300)
