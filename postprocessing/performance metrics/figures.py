import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(style="darkgrid")

results_dir = "../../results/development"
data_dir = os.environ['SIERRA_DATA_PATH']

figs_path = os.path.join(data_dir, 'results', 'figures', 'performance')
if not os.path.exists(figs_path):
    os.makedirs(figs_path)

sfpuc_gauges_filename = 'SFPUC_gauges_monthly.csv'


def create_timeseries_charts(basins, facilities, variables, filename, gauges_filename, dpi=600):
    print('creating {}'.format(filename))
    gauge_lookup = pd.read_csv('../../dashapp/gauges.csv', index_col=1, header=0, squeeze=True)
    gauge_to_node = gauge_lookup.to_dict()

    if '_mcm' in gauges_filename:
        ylabel = 'Storage (TAF)'
    else:
        ylabel = 'Flow (CFS)'

    dfs = []
    obs_dfs = []
    for var in variables:
        for basin in basins:
            basin_path = os.path.join(results_dir, basin, 'historical/Livneh')
            variable_path = os.path.join(basin_path, var + '.csv')
            if not os.path.exists(variable_path):
                print('skipping {} for {}'.format(var, basin))
                continue
            df = pd.read_csv(variable_path, header=0, index_col=0, skiprows=[1, 2], parse_dates=True)
            df.index.name = 'date'
            nodes = [c for c in df.columns if c in facilities]
            df = df[nodes]
            dfs.append(df)

            full_basin_name = basin.replace('_', ' ').title() + ' River'
            obs_path = os.path.join(data_dir, full_basin_name, 'gauges', gauges_filename)
            obs_df = pd.read_csv(obs_path, index_col=0, header=0, parse_dates=True)

            obs_df = obs_df.resample('MS').mean()
            if '_mcm' in gauges_filename:
                obs_df /= 1.2335

            if basin == 'tuolumne':
                sfpuc_path = os.path.join(data_dir, full_basin_name, 'gauges', sfpuc_gauges_filename)
                obs_df_sfpuc = pd.read_csv(sfpuc_path, index_col=0, header=0, parse_dates=True)

                # powerhouses = ['HolmPH', 'KirkwoodPH', 'MoccasinPH']
                # obs_df_sfpuc[powerhouses] /= 500
                obs_df_sfpuc['SJPL'] *= 1.547 # convert MGD to CFS

                obs_df = pd.concat([obs_df, obs_df_sfpuc], axis=1)

            obs_df.rename(columns=gauge_to_node, inplace=True)

            common_nodes = list(set(nodes) & set(obs_df.columns))
            if not common_nodes:
                print('no observed data for {} in {}'.format(var, basin))
            else:
                obs_dfs.append(obs_df[common_nodes])

    if not dfs:
        return

    df = pd.concat(dfs, axis=1)

    if obs_dfs:
        obs_df = pd.concat(obs_dfs, axis=1)
    else:
        obs_df = None

    # resample simulated data
    if '_mcm' in gauges_filename:
        # convert to TAF
        df /= 1.2335
    else:
        # convert to cfs
        df *= 1 / 0.0864 * 35.315
    df = df.resample('MS').mean()

    # match observed time steps to simulated
    if obs_df is not None:
        obs_df = obs_df.loc[df.index]

    df = df.reindex(columns=facilities)

    N = len(df.columns)
    fig, axes = plt.subplots(N, 1, figsize=(12, 3 * N))
    for i, node in enumerate(df.columns):
        ax = axes[i] if N > 1 else axes

        ax.plot(df.index, df[node], label='Simulated')

        if obs_df is not None and node in obs_df:
            ax.plot(obs_df.index, obs_df[node], label='Observed')

        # general
        ax.set_title(node, size=14)
        ax.set_xlabel('Date', size=12)
        ax.set_ylim(0)
        ax.set_ylabel(ylabel, size=12)
        if i == 0:
            ax.legend(ncol=1, loc='lower right')

    plt.show()

    fig_path = os.path.join(figs_path, filename)
    fig.savefig(fig_path, dpi=dpi)


if __name__ == '__main__':
    basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

    variables = ['Reservoir_Storage_mcm']
    # reservoirs = ['New Melones Lake', 'Don Pedro Reservoir', 'Lake McClure', 'Millerton Lake']
    # create_timeseries_charts(basins, reservoirs, variables, 'rim_reservoir_storage.png', 'storage_mcm.csv')

    # hh_storage_variables = ['Reservoir_Storage_mcm', 'Other_Storage_mcm']
    # hh_reservoirs = ['Hetch Hetchy Reservoir', 'Don Pedro Reservoir', 'Don Pedro Water Bank']
    # create_timeseries_charts(basins, hh_reservoirs, hh_storage_variables, 'hh_reservoir_storage.png', 'storage_mcm.csv')

    # hh_flow_variables = ['Hydropower_Flow_mcm', 'Output_Flow_mcm']
    # hh_flow_nodes = ['Kirkwood PH', 'Dion R Holm PH', 'Moccasin PH', 'SFPUC']
    # create_timeseries_charts(['tuolumne'], hh_flow_nodes, hh_flow_variables, 'hh_system_flow.png', 'streamflow_cfs.csv')
    #
    # create_timeseries_charts(
    #     ['tuolumne'],
    #     ['IFR bl Hetch Hetchy Reservoir', 'IFR bl Cherry Lake', 'IFR bl Lake Eleanor', 'IFR at La Grange'],
    #     ['InstreamFlowRequirement_Flow_mcm'],
    #     'hh_IFR_flow.png',
    #     'streamflow_cfs.csv'
    # )
    #
    # create_timeseries_charts(
    #     ['tuolumne'],
    #     ['Kirkwood PH', 'Moccasin PH', 'SFPUC'],
    #     ['Hydropower_Flow_mcm', 'Output_Flow_mcm'],
    #     'to_bay_flows.png',
    #     'streamflow_cfs.csv'
    # )
    #
    # create_timeseries_charts(
    #     ['tuolumne'],
    #     ['IFR bl Hetch Hetchy Reservoir', 'IFR at La Grange'],
    #     ['InstreamFlowRequirement_Flow_mcm'],
    #     'IFR_flows.png',
    #     'streamflow_cfs.csv'
    # )

    create_timeseries_charts(
        ['tuolumne'],
        ['IFR bl Cherry Lake', 'IFR bl Lake Eleanor'],
        ['InstreamFlowRequirement_Flow_mcm'],
        'IFR_flows_Cherry_Eleanor.png',
        'streamflow_cfs.csv'
    )

    create_timeseries_charts(
        ['tuolumne'],
        ['Cherry Lake', 'Lake Eleanor'],
        ['Reservoir_Storage_mcm'],
        'cherry_eleanor_storage.png',
        'storage_mcm.csv'
    )

