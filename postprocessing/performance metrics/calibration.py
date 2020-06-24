import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from hydroeval import evaluator, nse, kge, rmse, pbias

import datetime
from loguru import logger

sns.set(style="darkgrid")


def read_csv(path):
    return pd.read_csv(path, index_col=0, header=0, parse_dates=True)


results_path = os.environ['SIERRA_RESULTS_PATH']
data_path = os.environ['SIERRA_DATA_PATH']
validation_path = os.path.join(data_path, '..', 'validation')

gof_path = os.path.join(validation_path, 'goodness-of-fit')
if not os.path.exists(gof_path):
    os.makedirs(gof_path)

consolidated_path = os.path.join(validation_path, 'consolidated_results')
if not os.path.exists(consolidated_path):
    os.makedirs(consolidated_path)

start = '1980-10-01'
end = '2011-09-30'

flow_storage_gauges = pd.read_csv('../../dashapp/gauges.csv', index_col=0, header=0, squeeze=True)
energy_gauges = pd.read_csv('../../dashapp/gauges_lookup_energy.csv', index_col=0, header=0, squeeze=True)

aggs = {
    'Energy': 'sum',
    'Flow': 'mean',
    'Storage': 'mean'
}

units = {
    'Energy': 'MWh',
    'Flow': 'cfs',
    'Storage': 'taf'
}

sim_multipliers = {
    'Energy': 1,  # already in MWh
    'Flow': 1 / 0.0864 * 35.315,  # mcm to cfs
    'Storage': 1 / 1.2335  # mcm to taf
}

abbrs = {
    'stanislaus': 'STN',
    'tuolumne': 'TUO',
    'merced': 'MER',
    'upper_san_joaquin': 'USJ'
}

monthly_grouper = pd.Grouper(freq='MS', level=-1)
annual_grouper = pd.Grouper(freq='YS', level=-1)

today = datetime.datetime.now().strftime('%Y-%m-%d')
figures_path = os.path.join(results_path, 'figures', 'baseline', today)
if not os.path.exists(figures_path):
    os.makedirs(figures_path)

single_figs_path = os.path.join(figures_path, 'individual timeseries')
if not os.path.exists(single_figs_path):
    os.makedirs(single_figs_path)

obs_energy = read_csv('../../dashapp/monthly_hydro_1980_2018_MWh.csv')

filename_tpl = '{basin}_{attr}_{dim}_{timestep}_{style}_{n}.png'


def make_timeseries_fig(df, timestep, title=None):
    resources = sorted(list(set(df.index.get_level_values(0))))
    N = len(resources)
    n_max = 5
    x = 0
    if N > n_max:
        while 0 < N % n_max < 3 and x < 50:
            n_max += 1
            x += 1

    plots = range(0, N, n_max)
    for i, n in enumerate(plots):

        resources_subset = resources[n:n + n_max]
        df_subset = df.loc[resources_subset].reset_index()

        grid = sns.FacetGrid(df_subset, col="resource", hue="source", col_wrap=1, height=1.5, aspect=8, sharey=False)
        grid.map(sns.lineplot, "date", "value")
        # grid.map(label, "date")
        ylabel = '{} ({})'.format(dim, units.get(dim, unit))
        xlabel = 'Date'
        grid.set_axis_labels(xlabel, ylabel)
        grid.set_titles('{col_name}')
        grid.add_legend(title='')
        if title:
            full_title = title
            if N > 5:
                full_title += ' ({} of {})'.format(i + 1, len(plots))
            grid.fig.subplots_adjust(top=0.9)
            grid.fig.suptitle(full_title)
        # plt.show()

        figname = filename_tpl.format(
            basin=abbr, attr=attr, dim=dim, timestep=timestep, style='timeseries', n=i + 1
        )
        figdir = os.path.join(figures_path, '{}_timeseries'.format(timestep))
        if not os.path.exists(figdir):
            os.makedirs(figdir)
        figpath = os.path.join(figdir, figname)
        grid.fig.savefig(figpath, dpi=300)
        logger.info('Saved {}'.format(figname))

    plt.close('all')


def make_timeseries_figs(df_monthly):
    """
    Make time series figures
    :param df_monthly:
    :return:
    """

    # Monthly time series
    title = '{} {} {} {}'.format(basin_full, 'Monthly', attr, dim)
    make_timeseries_fig(df_monthly, 'monthly', title=title)

    # Annual time series
    level_values = df_monthly.index.get_level_values
    df_annual = df_monthly.groupby([level_values(i) for i in [0, 1]] + [annual_grouper]).agg(
        aggs.get(dim, 'mean'))
    title = '{} {} {} {}'.format(basin_full, 'Annual', attr, dim)
    make_timeseries_fig(df_annual, 'annual', title=title)


def calculate_performance_metrics():
    """

    :param df:
    :return:
    """

    excel_path = os.path.join(gof_path, 'all metrics.xlsx')
    with pd.ExcelWriter(excel_path) as xlwriter:

        for filename in os.listdir(consolidated_path):

            gof_df = pd.DataFrame(columns=['NSE', 'RMSE', 'PBIAS'])
            gof_df.index.name = 'resource'

            attr, dim, unit = filename.split('.')[0].split('_')
            file_path = os.path.join(consolidated_path, filename)
            df = pd.read_csv(file_path, index_col=[0, 1, 2], header=0)

            for resource, df0 in df.groupby(level=1):
                logger.info('Processing goodness-of-fit for {} {}'.format(resource, dim))
                df1 = df0.droplevel([0, 1], axis=0)

                for date in df1.index:
                    if pd.isna(df1.at[date, 'Observed']) or pd.isna(df1.at[date, 'Simulated']):
                        df1.drop(date, inplace=True)

                o = df1['Observed'].values
                s = df1['Simulated'].values
                nse_val = evaluator(nse, s, o)[0]
                rmse_val = evaluator(rmse, s, o)[0]
                pbias_val = evaluator(pbias, s, o)[0]
                gof_df.at[resource, 'NSE'] = round(nse_val, 2) if not pd.isna(nse_val) else 'nan'
                gof_df.at[resource, 'RMSE'] = round(rmse_val, 2) if not pd.isna(rmse_val) else 'nan'
                gof_df.at[resource, 'PBIAS'] = round(pbias_val, 2) if not pd.isna(pbias_val) else 'nan'

            csv_path = os.path.join(gof_path, '{} {}.csv'.format(attr, dim))

            gof_df.to_csv(csv_path)
            gof_df.to_excel(xlwriter, sheet_name='{} {}'.format(attr, dim))

    return


def consolidate_observed_and_simulated():
    all_dfs = {}

    for basin in ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']:
        # for basin in ['upper_san_joaquin']:

        basin_full = basin.title().replace('_', ' ') + ' River'

        hist_path = os.path.join(results_path, 'baseline', basin, 'historical', 'Livneh')

        basin_data_path = os.path.join(data_path, basin_full)

        for filename in os.listdir(hist_path):

            logger.info('Processing: {}, {}'.format(basin, filename))

            # get metadata
            abbr = abbrs[basin]
            attr, dim, unit = filename.split('.')[0].split('_')

            # get simulated values
            filepath = os.path.join(hist_path, filename)
            try:
                sim = read_csv(filepath) * sim_multipliers.get(dim, 1)
            except:
                logger.error('Failed to read {}'.format(filepath))
                continue

            sim = sim.loc[start:end]

            # get observed values
            resources = list(sim.columns)
            obs = None
            if dim == 'Flow':
                obs = read_csv(os.path.join(basin_data_path, 'gauges', 'streamflow_cfs.csv')).loc[start:end]
            elif dim == 'Storage':
                obs = read_csv(os.path.join(basin_data_path, 'gauges', 'storage_mcm.csv')).loc[start:end] / 1.2335
            elif dim == 'Energy':
                obs = obs_energy.copy()

            if obs is None:
                logger.warning('No observed values for {}'.format(filepath))
                continue

            if dim == 'Energy':
                gauges = energy_gauges
            else:
                gauges = flow_storage_gauges

            attr_gauges = {gauges[res]: res for res in resources if res in gauges and gauges[res] in obs}
            obs = obs[list(attr_gauges.keys())]
            obs = obs.rename(columns=attr_gauges)

            # munge data
            sim = sim.unstack().to_frame()
            sim.columns = ['value']
            sim.index.names = ['resource', 'date']
            sim_level_values = sim.index.get_level_values
            try:
                sim = sim.groupby([sim_level_values(0)] + [monthly_grouper]).agg(aggs.get(dim, 'mean'))
            except:
                logger.error('Unable to group {}'.format(filepath))
                continue

            obs = obs.unstack().to_frame()
            obs.columns = ['value']
            obs.index.names = ['resource', 'date']

            if dim != 'Energy':
                obs_level_values = obs.index.get_level_values
                try:
                    obs = obs.groupby([obs_level_values(0)] + [monthly_grouper]).agg(aggs.get(dim, 'mean'))
                except:
                    logger.error('Unable to group observed {} {} for {}'.format(attr, dim, basin))
                    continue

            index_names = ['resource', 'source', 'date']

            df_monthly = obs.join(sim, on=['resource', 'date'], how='right', lsuffix='.obs',
                                  rsuffix='.sim').reset_index()
            df_monthly.columns = ['resource', 'date', 'Observed', 'Simulated']
            df_monthly = df_monthly.set_index(['resource', 'date']).stack().to_frame().reset_index()
            df_monthly.columns = ['resource', 'date', 'source', 'value']
            df_monthly.set_index(index_names, inplace=True)

            # Basic time series figures
            # make_timeseries_figs(df_monthly)

            df_monthly['basin'] = basin
            df_monthly = df_monthly \
                .reset_index() \
                .set_index(['basin', 'resource', 'source', 'date']) \
                .unstack('source') \
                .droplevel(0, axis=1)

            all_dfs[filename] = all_dfs.get(filename, []) + [df_monthly]

    for filename, dfs in all_dfs.items():
        filepath = os.path.join(consolidated_path, filename)
        pd.concat(dfs).to_csv(filepath)


if __name__ == '__main__':
    # consolidate_observed_and_simulated()

    # Performance metrics
    calculate_performance_metrics()

print('done!')
