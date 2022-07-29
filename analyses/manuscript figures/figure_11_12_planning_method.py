import os
import datetime as dt
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setup
output_dir = os.environ.get('SIERRA_RESULTS_PATH', '../../results')
basin = 'stanislaus'
hydrology_scenario = 'historical/Livneh'

year = 1990
n = 3
start = dt.datetime(year, 10, 1)
end = dt.datetime(year + n, 9, 30)
start_months = [
    (dt.datetime(year, 10, 1), dt.datetime(year + 1, 2, 1)),
    (dt.datetime(year + 1, 1, 1), dt.datetime(year + 1, 5, 1))
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
    'flow': r'Flow ($million\/m^3/day$)'
}

subplot_letters = [['a', 'b'], ['c', 'd']]

sns.set_style('whitegrid')

plt.rcParams.update({
    "text.usetex": False,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"]})

fontsize = 12


def get_planning_df():
    run_name = 'planning method'
    basin_path = os.path.join(output_dir, run_name, basin, r'historical\Livneh')
    file_path = os.path.join(basin_path, 'planning_model_results.csv')
    df = pd.read_csv(file_path, index_col=[0, 1], parse_dates=True, header=[0], skiprows=[1, 2])
    df.index.names = ['month', 'planning month']
    return df


# Planning example

def plot_optimal(N=3):
    sns.set_palette('Set1')

    df = get_planning_df()

    months = df.index.levels[0]
    fig, axes = plt.subplots(2, 2, figsize=(12, 5))

    for i, param in enumerate(['storage', 'flow']):
        facilities = facility_groups[i]
        for j, (start_month, end_month) in enumerate(start_months):
            ax = axes[i, j]
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

            if (i, j) in [(0, 0), (0, 1)]:
                ax.legend(title='Start date', fontsize=fontsize)

            if len(facilities) > 1:
                facility_name = 'Aggregated {}'.format(param)
            else:
                facility_name = facilities[0].replace('PH', 'Powerhouse')

            subplot_title = '{}) {} ({})'.format(subplot_letters[i][j], facility_name, start_month_str)
            ax.set_title(subplot_title, fontsize=fontsize + 1)
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


# Planning vs. scheduled - daily

def plot_simulated(resolution='daily'):
    # sns.set_palette(['grey', 'blue', 'green'])
    sns.set_palette('bright')

    fig, axes = plt.subplots(2, 1, figsize=(12, 6))

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
            file_path = os.path.join(output_dir, run_nome, basin, hydrology_scenario, var_filename)
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
        run_names = 'no planning'
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
        if i == 0:
            ax.legend(title='', loc='lower right')
        else:
            ax.legend().remove()
    fig.autofmt_xdate()
    fig.savefig(f'figure - comparisons - {resolution}.png', dpi=600, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    plot_optimal()
    plot_simulated('daily')
    plot_simulated('monthly')
