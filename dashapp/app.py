# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import os
import json
from itertools import product
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objs as go
import seaborn as sns

import dash_daq as daq

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

opath = '../data/{basin}/gauges/{attr}.csv'
# PROD_RESULTS_PATH = r'C:\Users\david\Box\CERC-WET\Task7_San_Joaquin_Model\Pywr models\results'
PROD_RESULTS_PATH = r'C:\data'
# PROD_RESULTS_PATH = '../results'
DEV_RESULTS_PATH = '../results'
PATH_TEMPLATES = {
    'mcm': '{run}/{basin}/{scenario}/{res_type}_{res_attr}_mcm.csv',
    'Variable Head': '{run}/{basin}/{scenario}/{res_type}_{res_attr}_m.csv',
}

OBSERVED_TEXT = 'Observed'
OBSERVED_COLOR = 'lightgrey'

MCM_TO_CFS = 1e6 / 24 / 3600 * 35.31
MCM_TO_TAF = 1 / 1.2335

AXIS_LABELS = {
    'storage': 'Storage (TAF)',
    'flow': 'Flow (cfs)',
    'generation': 'Generation (MWh)',
    'M': 'Month',
    'Y': 'Year'
}

PLOTLY_CONFIG = {
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['toggleSpikelines', 'sendDataToCloud', 'autoScale2d', 'zoomOut2d', 'zoomIn2d',
                               'editInChartStudio', 'boxSelect',
                               'lassoSelect'],
    'showLink': False,
}

BASINS = {
    'stn': 'Stanislaus',
    'tuo': 'Tuolumne',
    'mer': 'Merced',
    'usj': 'Upper San Joaquin'
}

source_text = {'simulated': 'Simulated', 'observed': 'Observed'}
# source_name = {'simulated': 'Simulated'}
source_color = {'simulated': 'blue', 'observed': 'darkgrey'}

PALETTES = {
    'P2009': 'Blues_r',
    'P2030': 'BuGn_r',
    'P2060': 'OrRd_r'
}

GCMS = ['Livneh', 'HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
RCPS = ['rcp45', 'rcp85']


def flow_to_energy(df_cfs, head):
    # df comes in as cfs...
    # MWh = Q[cms] * head[m] * eta * g[m/s^s] * rho[kg/m^3] * hours in day / 1e6
    df = df_cfs / 35.31 * head * 0.9 * 9.81 * 1000 * 24 / 1e6
    return df


def get_plot_kwargs(source):
    return dict(
        mode='lines',
        opacity=0.7,
        # line_color=source_color[source]
    )


RES_OPTIONS = {}
SCENARIOS = {}

ENSEMBLE_NAMES = {
    'mer': {
        'SWRCB 40': ['Baseline', '10%', '20%', '30%', '40%'],
        'District Reductions': ['Baseline', 'Reductions']
    },
    'stn': {
        'Price Year': ['PY2009', 'PY2060'],
        'SWRCB 40': ['Baseline', '40%'],
    }
}


# =================

def register_basin_callbacks(basin, scenarios):
    scenario_inputs = [Input(s['name'].replace(' ', '-'), 'value') for s in scenarios]

    @app.callback(Output('{}-tabs-content'.format(basin), 'children'),
                  [
                      Input('development-tabs', 'active_tab'),
                      Input('radio-transform', 'value'),
                      Input('radio-resample', 'value'),
                      Input('radio-aggregate', 'value'),
                      Input('percentiles-checklist', 'value'),
                      Input('percentiles-options', 'value'),
                      Input('percentiles-type', 'value'),
                      Input('select-basin', 'value'),
                      Input('select-climate', 'value'),
                      Input('select-rcp', 'value'),
                      Input('select-resources', 'value'),
                      Input('reload', 'n_clicks')
                  ] + scenario_inputs)
    def render_scenarios_content(
            tab, transform, resample, aggregate, consolidate, percentiles, percentiles_type, basin, climates, rcps,
            resources, n_clicks,
            *args):
        selected_scenarios = args
        kwargs = dict(
            basin=basin,
            climates=climates,
            rcps=rcps,
            resources=resources,
            transform=transform,
            resample=resample,
            aggregate=aggregate,
            consolidate=consolidate,
            percentiles=percentiles,
            percentiles_type=percentiles_type,
            run_name='full run 2019-12-19',
            selected_scenarios=selected_scenarios
        )
        return render_timeseries_collection(tab, **kwargs)


obs_storage = []
obs_streamflow = []

for basin in ['stn', 'tuo', 'mer', 'usj']:
    RES_OPTIONS[basin] = {}
    basin_long = BASINS[basin].replace(' ', '_').lower()
    with open('../{}/pywr_model.json'.format(basin_long)) as f:
        m = json.load(f)
    nodes = {n['name']: n for n in m['nodes']}

    # load scenarios
    price_scenario = {
        'name': 'Price Year',
        'size': 2
    }
    basin_scenarios = [price_scenario] + m.get('scenarios', [])
    SCENARIOS[basin] = basin_scenarios

    for recorder in m['recorders']:
        parts = recorder.split('/')
        if len(parts) == 2:
            res, attr = parts
            node = nodes.get(res)
            if not node:
                continue
            ta = (node['type'], attr)
            option = {'label': res, 'value': res.replace(' ', '_')}
            if ta in RES_OPTIONS[basin]:
                RES_OPTIONS[basin][ta].append(option)
            else:
                RES_OPTIONS[basin][ta] = [option]

    # load observed data
    attr = 'storage_af'
    if basin in ['stn', 'usj']:
        attr = 'storage_mcm'
    try:
        df = pd.read_csv(
            opath.format(basin=basin_long.replace('_', ' ').title() + ' River', attr=attr),
            index_col=[0],
            parse_dates=True
        ).ffill()
        if '_mcm' in attr:
            df *= MCM_TO_TAF
        else:
            df /= 1000
        obs_storage.append(df)
    except:
        pass

    df = pd.read_csv(
        opath.format(basin=basin_long.replace('_', ' ').title() + ' River', attr='streamflow_cfs'),
        index_col=[0],
        parse_dates=True
    ).ffill()  # already cfs, no need to concert
    obs_streamflow.append(df)

    # register basin callbacks
    register_basin_callbacks(basin, basin_scenarios)

df_obs_storage = pd.concat(obs_storage, axis=1)
df_obs_streamflow = pd.concat(obs_streamflow, axis=1)

gauge_lookup = pd.read_csv('gauges.csv', index_col=[0], squeeze=True, dtype=(str)).to_dict()
gauge_number_to_name = {}
for gauge in df_obs_streamflow.columns:
    if 'USGS' in gauge:
        gauge_number_to_name[gauge.split(' ')[1]] = gauge
for loc, gauge in gauge_lookup.items():
    if gauge in gauge_number_to_name:
        gauge_lookup[loc] = gauge_number_to_name[gauge]


def root_mean_square_error(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def nash_sutcliffe_efficiency(predictions, targets):
    if not predictions.any() or not targets.any():
        return -1
    slope, intercept, r_value, p_value, std_err = stats.linregress(predictions, targets)
    return r_value ** 2


def percent_bias(predictions, targets):
    return predictions.mean() / targets.mean() - 1


def load_timeseries_old(results_path, basin, forcings, res_type, res_attr, nscenarios=1,
                        run='full run', tpl='mcm', multiplier=1.0):
    path_tpl = os.path.join(results_path, PATH_TEMPLATES[tpl])
    collection = []
    for forcing in forcings:
        path = path_tpl.format(
            basin=BASINS[basin].replace(' ', '_').lower(),
            run=run,
            scenario=forcing,
            res_type=res_type,
            res_attr=res_attr
        )
        if not os.path.exists(path):
            continue
        header = list(range(nscenarios + 1))
        df = pd.read_csv(
            path,
            index_col=[0],
            parse_dates=True,
            header=header
        ) * multiplier
        for i, scenario in enumerate(SCENARIOS[basin]):
            ensemble_names = ENSEMBLE_NAMES[basin][scenario['name']]
            df.columns.set_levels(ensemble_names, level=i + 1, inplace=True)
        if run == 'development':
            df.columns = df.columns.droplevel(header[1:])
        df.name = forcing
        collection.append(df)
    if collection:
        return pd.concat(collection, axis=1, keys=forcings)
    else:
        return None


def load_timeseries_new(results_path, basin, forcings, res_type, res_attr, nscenarios=1,
                        run='full run', tpl='mcm', multiplier=1.0, aggregate=None, filterby=None):
    full_basin = BASINS[basin].replace(' ', '_').lower()
    if run == 'development':
        path_tpl = os.path.join(results_path, PATH_TEMPLATES[tpl])
        path = path_tpl.format(
            run=run,
            basin=full_basin,
            scenario=forcings[0],
            res_type=res_type,
            res_attr=res_attr
        )
        if not os.path.exists(path):
            return None

        scenarios = SCENARIOS[basin]
        header = list(range(len(scenarios) + 1))

        df = pd.read_csv(path, index_col=0, parse_dates=True, header=header)

        start = 1
        end = start + len(df.columns.names[1:-1])
        levelvals = df.columns.levels[start:end+1]
        for i, val in enumerate(levelvals):
            df.drop(val[1:], axis=1, level=1, inplace=True)
            df = df.droplevel(1, axis=1)
        new_levels = [(forcings[0], col) for col in df.columns]
        df.columns = pd.MultiIndex.from_tuples(new_levels)

    else:
        path = os.path.join(results_path, '{}.h5'.format(full_basin))
        key = '{}_{}_mcm'.format(res_type, res_attr).replace(' ', '_')
        df = pd.read_hdf(path, key=key)

        for i, scenario in enumerate(SCENARIOS[basin]):
            ensemble_names = ENSEMBLE_NAMES[basin][scenario['name']]
            df.columns.set_levels(ensemble_names, level=i + 2, inplace=True)

    if filterby:
        resources = [s.replace('_', ' ') for s in filterby]
        idx = pd.IndexSlice
        df = df.loc[:, idx[:, resources]]

    if df.empty:
        return None

    if aggregate:
        df = agg_by_resources(df, aggregate)

    df *= multiplier

    return df


def load_timeseries(*args, **kwargs):
    return load_timeseries_new(*args, **kwargs)


def consolidate_dataframe(df, resample):
    if not resample:
        fmt = '%j'
    else:
        fmt = '%m'
    _df = df.copy()
    _df.index = pd.MultiIndex.from_tuples([(date.strftime(fmt), str(date.year)) for date in df.index])
    _df = _df.unstack(level=-1)
    if not resample:
        dates = pd.date_range(start='2000-01-01', periods=len(_df.index), freq='D')
        _df.index = [d.strftime('%b-%d') for d in dates]
    else:
        dates = pd.date_range(start='2000-01-01', periods=len(_df.index), freq='MS')
        _df.index = [d.strftime('%b') for d in dates]
    return _df


percentile_colors = {
    'simulated': 'blue',
    'observed': 'grey'
}

percentiles_ordered = {
    ('median', 'quartiles'): ['quartiles', 'median'],
    ('median', 'quartiles', 'range'): ['range', 'quartiles', 'median'],
    ('quartiles', 'range'): ['range', 'quartiles'],
    ('median', 'range'): ['range', 'median']
}


def percentile_timeseries_graphs(df, name, options, color='black'):
    pcts = []
    show_mean = False
    percentiles = options[:]
    if 'mean' in options:
        show_mean = True
        percentiles.pop(options.index('mean'))

    pct_set = tuple(set(percentiles))

    span_pcts = {
        'median': [0.5],
        'quartiles': [0.25, 0.75],
        'range': [0.0, 1.0]
    }

    lines = []
    for i, span in enumerate(percentiles_ordered.get(pct_set, list(pct_set))):
        pcts = span_pcts[span]
        for j, pct in enumerate(pcts):
            fill = None
            showlegend = i == 0
            width = 2
            opacity = 0.0
            if len(pcts) > 1:
                width = 0
                if j == 0:
                    showlegend = False
                elif j == 1:
                    fill = 'tonexty'
            lines.append(
                go.Scatter(
                    x=df.index,
                    y=df.quantile(pct, axis=1),
                    showlegend=showlegend,
                    mode='lines',
                    fill=fill,
                    text='{}: {}%'.format(name, pct * 100),
                    name=name,
                    line=dict(color=color, width=width)
                )
            )
    if show_mean:
        lines.append(
            go.Scatter(
                x=df.index,
                y=df.mean(axis=1),
                showlegend=False,
                mode='lines',
                text='{} mean'.format(name),
                name=name,
                # line=dict(color=color, width=3)
            )
        )

    return lines


def boxplots_graphs(df, name, percentiles, color='black'):
    plot = go.Box(
        y=df.values.flatten(),
        name=name,
    )
    return [plot]


def indicator(id, label, value, color):
    return html.Div(
        [
            label + ': ', value,
            daq.Indicator(
                color=color,
                value=True
            )
        ],
        id=id,
        style={'display': 'inline-block'}
    )


def timeseries_component(attr, res_name, all_sim_vals, df_obs, **kwargs):
    res_name_id = res_name.lower().replace(' ', '_')
    ts_data = []
    fd_data = []

    resample = kwargs.get('resample')
    percentiles = kwargs.get('percentiles')
    consolidate = kwargs.get('consolidate')
    calibration = kwargs.get('calibration')
    climates = kwargs.get('climates')
    rcps = kwargs.get('rcps')
    percentiles_type = kwargs.get('percentiles_type', 'timeseries')
    scenario_combos = kwargs.get('scenario_combos', [])
    head = kwargs.get('head')

    color_idx = -1

    for i, forcing in enumerate(set(all_sim_vals.columns.get_level_values(0))):
        parts = forcing.split('_')
        rcp = None
        if len(parts) == 1:
            gcm, = parts
        else:
            gcm, rcp = parts

        if climates and gcm not in climates:
            continue

        if 'Livneh' not in forcing and rcps and rcp not in rcps:
            continue

        # sim_color = sns.color_palette(PALETTES[priceyear]).as_hex()[GCMS.index(gcm)]
        # sim_color = sns.color_palette().as_hex()[i]
        # sim_color = None
        resource_scenario_sim_vals = all_sim_vals[forcing, res_name]
        # for multiindex in resource_scenario_sim_vals.columns:
        #     sim_vals = resource_scenario_sim_vals[multiindex]
        for scenario_combo in scenario_combos:

            color_idx += 1
            sim_color = sns.color_palette().as_hex()[color_idx]

            if scenario_combo:
                scenario_name = '{} {}'.format(tuple(parts), scenario_combo)
            else:
                scenario_name = '{}'.format(tuple(parts))

            if not scenario_combo:
                sim_vals = resource_scenario_sim_vals
            else:
                if len(scenario_combo) == 1:
                    sim_vals = resource_scenario_sim_vals[scenario_combo[0]]
                else:
                    sim_vals = resource_scenario_sim_vals[scenario_combo]
            if gcm == 'Livneh':
                sim_vals = sim_vals[sim_vals.index.year < 2020]
            else:
                sim_vals = sim_vals[sim_vals.index.year >= 2020]
            if head is not None:
                sim_vals = flow_to_energy(sim_vals, head)
            if resample:
                sim_resampled = sim_vals.dropna().resample(resample).mean()
            else:
                sim_resampled = sim_vals.dropna()

            plot_max = False
            max_reqt = kwargs.get('max_reqt')
            if max_reqt is not None and res_name in max_reqt[forcing]:
                plot_max = True

            # Minimum flow requirement
            min_reqt = kwargs.get('min_reqt')
            if not consolidate and min_reqt is not None and res_name in min_reqt[forcing]:
                if resample:
                    min_reqt_resampled = min_reqt.resample(resample).mean()
                else:
                    min_reqt_resampled = min_reqt.copy()
                ts_data.append(
                    go.Scatter(
                        x=min_reqt_resampled[forcing].index,
                        y=min_reqt_resampled[forcing][res_name],
                        text='Min Requirement',
                        mode='lines',
                        opacity=0.7,
                        # opacity=0.7 if not plot_max else 0.0,
                        name='Min Requirement',
                        line_color='red'
                    )
                )

            # Maximum flow requirement
            if not consolidate and plot_max:
                ts_data.append(
                    go.Scatter(
                        x=max_reqt[forcing].index,
                        y=max_reqt[forcing][res_name],
                        text='Max Requirement',
                        mode='lines',
                        fill='tonexty',
                        opacity=0.7,
                        name='Max Requirement',
                        line_color='lightblue',
                        line=dict(width=0.5)
                    )
                )

            if consolidate:
                try:
                    sim_cons = consolidate_dataframe(sim_resampled, resample)
                except:
                    print('Failed to consolidate: ', forcing)
                    continue
                if percentiles_type == 'timeseries':
                    sim_vals = sim_cons.quantile(0.5, axis=1)
                    sim_data = percentile_timeseries_graphs(sim_cons, scenario_name, percentiles, color=sim_color)
                else:
                    sim_data = boxplots_graphs(sim_cons, scenario_name, percentiles, color=sim_color)
                ts_data.extend(sim_data)

            else:
                ts_data.append(
                    go.Scatter(
                        x=sim_resampled.index,
                        y=sim_resampled.values,
                        text=scenario_name,
                        mode='lines',
                        opacity=0.7,
                        name=scenario_name,
                        line=dict(color=sim_color)
                    )
                )

            N = len(sim_resampled)
            fd_data.append(
                go.Scatter(
                    y=sorted(sim_resampled.values),
                    x=np.arange(0, N) / N * 100,
                    name=scenario_name,
                    text=scenario_name,
                    # line=dict(color=sim_color),
                    mode='lines',
                    opacity=0.7,
                )
            )

    gauges = []
    gauge_name = gauge_lookup.get(res_name, res_name)
    pbias = 100
    nse = -1

    if calibration and gauge_name in df_obs:
        obs_vals = df_obs[gauge_name]

        head = kwargs.get('head')
        if head:
            obs_vals = flow_to_energy(obs_vals, head)

        if not consolidate:  # percentiles values will use the whole record
            obs_vals = obs_vals.loc[sim_vals.index]

        if resample:
            obs_resampled = obs_vals.resample(resample, axis=0).mean()
        else:
            obs_resampled = obs_vals

        if consolidate:  # use original values
            obs_cons = consolidate_dataframe(obs_resampled, resample)
            obs_vals = obs_cons.quantile(0.5, axis=1)  # for use in flow-duration curve

        # flow-duration curve
        N = len(obs_vals)
        fd_data.insert(0,
                       go.Scatter(
                           y=sorted(obs_vals.values),
                           x=np.arange(0, N) / N * 100,
                           name=OBSERVED_TEXT,
                           text=OBSERVED_TEXT,
                           mode='lines',
                           opacity=0.7,
                           line=dict(color=OBSERVED_COLOR)
                       )
                       )

        if consolidate:
            predictions = sim_resampled.values
            targets = obs_resampled.loc[sim_resampled.index].values
        else:
            predictions = sim_vals.values
            targets = obs_vals.loc[sim_vals.index].values

        pbias = percent_bias(predictions, targets) * 100
        # rmse = root_mean_square_error(predictions, targets)
        nse = nash_sutcliffe_efficiency(predictions, targets)

        if consolidate:
            obs_data = None
            if percentiles_type == 'timeseries':
                obs_data = percentile_timeseries_graphs(obs_cons, OBSERVED_TEXT, percentiles, color=OBSERVED_COLOR)
            elif percentiles_type == 'boxplot':
                obs_data = boxplots_graphs(obs_cons, OBSERVED_TEXT, percentiles, color=OBSERVED_COLOR)
            ts_data.extend(obs_data)
        else:
            obs_graph = go.Scatter(
                x=obs_resampled.index,
                y=obs_resampled,
                text=OBSERVED_TEXT,
                mode='lines',
                opacity=0.7,
                name=OBSERVED_TEXT,
                line=dict(color=OBSERVED_COLOR)
            )
            ts_data.insert(0, obs_graph)

    if calibration:
        if nse <= 0:
            nse_color = 'red'
        elif nse <= 0.5:
            nse_color = 'orange'
        else:
            nse_color = 'green'

        GAUGE_SIZE = 80

        nse_gauge = daq.Gauge(
            id='nse-gauge-' + res_name_id,
            label='NSE',
            size=GAUGE_SIZE,
            min=-1.0,
            value=nse,
            max=1.0,
            color=nse_color,
        )
        # nse_gauge = indicator(
        #     id='nse-gauge-' + res_name_id,
        #     label='NSE',
        #     value=round(nse, 2),
        #     color=nse_color,
        # )

        if abs(pbias) >= 20:
            pbias_color = 'red'
        elif abs(pbias) >= 10:
            pbias_color = 'orange'
        else:
            pbias_color = 'green'

        pbias_gauge = daq.Gauge(
            id='pbias-gauge-' + res_name_id,
            label='% bias',
            size=GAUGE_SIZE,
            min=min(pbias, -100.0),
            value=pbias,
            max=max(pbias, 100.0),
            color=pbias_color
        )
        # pbias_gauge = indicator(
        #     id='pbias-gauge-' + res_name_id,
        #     label='% bias',
        #     value=round(pbias, 2),
        #     color=pbias_color
        # )

        gauges = html.Div(
            [nse_gauge, pbias_gauge]
        )

    ylabel = AXIS_LABELS.get(attr, 'unknown')

    timeseries_graph = dcc.Graph(
        id='timeseries-' + res_name_id,
        className='timeseries-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': ts_data,
            'layout': go.Layout(
                title='Timeseries',
                xaxis={'title': AXIS_LABELS.get(resample, "Date"), 'tickangle': -45},
                yaxis={'title': ylabel, 'rangemode': 'tozero'},
                margin={'l': 60, 'b': 80, 't': 40, 'r': 10},
                legend={'x': 0.02, 'y': 0.98},
                hovermode='closest',
                yaxis_type=kwargs.get('transform', 'linear'),
            ),
        },

    )

    flow_duration_graph = dcc.Graph(
        id='flow-duration-' + res_name_id,
        className='flow-duration-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': fd_data,
            'layout': go.Layout(
                title='{}-duration'.format(attr.title()),
                xaxis={'title': 'Duration (%)'},
                yaxis={'title': ylabel},
                margin={'l': 60, 'b': 80, 't': 40, 'r': 10},
                legend={'x': 0.05, 'y': 0.95},
                hovermode='closest',
                yaxis_type=kwargs.get('transform', 'linear')
            )
        },
    )

    children = [timeseries_graph, flow_duration_graph]

    div = html.Div(
        # key='{}'.format(consolidate),
        children=[
            html.H5(res_name),
            html.Div(
                children=children,
                className="timeseries-metrics-data",
            )
        ],
        className="timeseries-metrics-box"
    )

    return div


def gauges_content(**kwargs):
    gauges = []
    ts_data = []
    for gauge in gauges:
        ts_data.append(
            go.Scatter(
                x=df_obs_streamflow.index,
                y=df_obs_streamflow[gauge],
                text=gauge,
                mode='lines',
                opacity=0.7,
                name=gauge,
                # line=go.scatter.Line(color=source_color[source])
            )
        )
    timeseries_graph = dcc.Graph(
        id='gauges-all',
        className='timeseries-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': ts_data,
            'layout': go.Layout(
                title='Timeseries',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Flow', 'rangemode': 'tozero'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                yaxis_type=kwargs.get('transform', 'linear')
            )
        }
    )

    return html.Div(
        [timeseries_graph]
    )


THEMES = [
    'Bootstrap',
    'Darkly'
]


def render_themes(selected=None):
    return [dbc.RadioItems(
        id="select-theme",
        options=[{"label": theme, "value": theme} for theme in THEMES],
        value=selected
    )]


navbar = dbc.NavbarSimple(
    children=[
        dcc.Dropdown(
            id='select-basins-global',
            options=[
                {'label': 'Stanislaus', 'value': 'stn'},
                {'label': 'Tuolumne', 'value': 'tuo'},
                {'label': 'Merced', 'value': 'mer'},
                {'label': 'Upper San Joaquin', 'value': 'usj'},
            ],
            value=['stn', 'tuo', 'mer', 'usj'],
            multi=True
        )
        # dbc.NavItem(dbc.NavLink("Link", href="#")),
        # dbc.DropdownMenu(
        #     nav=True,
        #     in_navbar=True,
        #     id='select-themes',
        #     label="Theme",
        #     children=render_themes(),
        # ),
    ],
    brand="San Joaquin Dashboard",
    brand_href="#",
    # sticky="top",
)

transform_radio = dbc.FormGroup(
    [
        dbc.Label("Transform", html_for="radio-transform", width=2),
        dbc.RadioItems(
            id="radio-transform",
            options=[
                {"label": "Linear", "value": 'linear'},
                {"label": "Log", "value": 'log'},
            ],
            value='linear',
            # inline=True
        ),
    ],
)

resample_radio = dbc.FormGroup(
    [
        dbc.Label("Resampling", html_for="radio-resample", width=2),
        dbc.RadioItems(
            id="radio-resample",
            options=[
                {"label": "None", "value": None},
                {"label": "Monthly", "value": 'MS'},
                {"label": "Annual", "value": 'Y'},
            ],
            value="MS",
            # inline=True
        ),
    ],
)

aggregate_radio = dbc.FormGroup(
    [
        dbc.Label("Aggregation", html_for="radio-aggregate", width=2),
        dbc.RadioItems(
            id="radio-aggregate",
            options=[
                {"label": "None", "value": None},
                {"label": "Mean", "value": 'mean'},
                {"label": "Sum", "value": 'sum'},
            ],
            value=None,
        ),
    ],
)

consolidation_checklist = dbc.FormGroup(
    [
        dbc.Checklist(
            id="percentiles-checklist",
            options=[
                {"id": "percentiles-checkbox", "label": "Percentiles", "value": "consolidate"}
            ],
            value=["consolidate"],
        ),
        dbc.RadioItems(
            id="percentiles-type",
            options=[],
            value='timeseries'
        ),
        dbc.Checklist(
            id="percentiles-options",
            options=[],
            value=["median", "quartiles"],
        ),
    ],
)

select_development_basin = dcc.Dropdown(
    id="select-basin",
    options=[],
    value=None,
    style={'min-width': '200px'},
    placeholder="Select a basin..."
)

select_climate = dcc.Dropdown(
    className="select-climate",
    id="select-climate",
    options=[
        {"label": "Livneh", "value": "Livneh"},
        {"label": "CanESM2", "value": "CanESM2"},
        {"label": "CNRM-CM5", "value": "CNRM-CM5"},
        {"label": "HadGEM2-ES", "value": "HadGEM2-ES"},
        {"label": "MIROC5", "value": "MIROC5"},
    ],
    multi=True,
    value=["Livneh"]
)

select_rcp = dcc.Dropdown(
    className="select-climate",
    id="select-rcp",
    options=[
        {"label": "RCP 4.5", "value": "rcp45"},
        {"label": "RCP 8.5", "value": "rcp85"}
    ],
    multi=True,
    value=["rcp85"]
)

scenarios_selections = dbc.Form([
    dbc.FormGroup([
        select_development_basin, select_climate, select_rcp
    ])
], inline=True, style={"margin-bottom": "10px"})

development_selections = dbc.Form([
    dbc.FormGroup([
        select_development_basin
    ])
], inline=True, style={"margin-bottom": "10px"})

controls = dbc.Form(
    [transform_radio, resample_radio, aggregate_radio, consolidation_checklist],
    inline=False
)

top_bar = dbc.Form(
    [
        dbc.FormGroup([
            dcc.Dropdown(
                options=[],
                id='select-resources',
                className='select-resources',
                style={'min-width': '300px'},
                multi=True,
                value=[],
                placeholder='Select a resource...'
            ),
            dbc.Button([
                'Reload'
            ], id='reload', style={'margin-left': 'auto'})
        ], style={'display': 'inline-flex', 'margin-top': '5px', 'width': '100%'})
    ]
)


def development_content(purpose):
    if purpose == "development":
        selections = development_selections
        scenario_selections = None
        main_content = html.Div(
            id='development-tabs-content',
            style={'padding': '10px'},
            children=[]
        )
    else:
        selections = scenarios_selections
        main_content = html.Div(
            id='tabs-content',
            style={'padding': '10px'},
            children=[]
        )
        scenario_selections = html.Div([], id='scenario-selections')
    return dbc.Row([
        dbc.Col([
            html.Div(children=[
                selections,
                scenario_selections,
                dbc.Tabs(id="development-tabs", active_tab='system', children=[
                    dbc.Tab(label='System', tab_id='system'),
                    dbc.Tab(label='Reservoir storage', tab_id='reservoir-storage'),
                    dbc.Tab(label='HP flow', tab_id='hydropower-flow'),
                    dbc.Tab(label='HP generation', tab_id='hydropower-generation'),
                    dbc.Tab(label='IFR flow', tab_id='ifr-flow'),
                    # dbc.Tab(label='IFR flow (range)', tab_id='ifr-range-flow'),
                    dbc.Tab(label='Outflow', tab_id='outflow')
                ]),
                top_bar,
                main_content
            ])],
            width=11
        ),
        dbc.Col([
            html.Div([
                controls
            ])
        ], width=1)
    ])


def get_resources_old(df, filterby=None):
    all_resources = sorted(set(df.columns.get_level_values(1)))
    return [r for r in all_resources if not filterby or r.replace(' ', '_') in filterby]


def get_resources(df, filterby=None):
    all_resources = sorted(set(df.columns.get_level_values(1)))
    # return [r for r in all_resources if not filterby or r.replace(' ', '_') in filterby]
    return all_resources


def agg_by_resources(df, agg):
    levels = list(range(len(df.columns.levels)))
    levels.pop(1)
    df = df.groupby(axis=1, level=levels).agg(agg)
    new_cols = [(c[0], agg) + tuple(c[1:]) for c in df.columns]
    df.columns = pd.MultiIndex.from_tuples(new_cols)
    return df


def render_timeseries_collection(tab, **kwargs):
    children = []
    resources = kwargs.pop('resources', None)
    selected_scenarios = kwargs.pop('selected_scenarios', [])
    consolidate = "consolidate" in kwargs.get('consolidate', [])
    kwargs['consolidate'] = consolidate

    resample = kwargs.get('resample')
    aggregate = kwargs.get('aggregate')
    basin = kwargs.get('basin')
    if not basin:
        return ["Select a basin."]

    climates = kwargs.get('climates')
    rcps = kwargs.get('rcps')
    calibration = climates is None
    run_name = kwargs.get('run_name', 'development')

    load_data_kwargs = dict(
        run=run_name,
        nscenarios=max(len(SCENARIOS.get(basin, [])), 1),
        aggregate=aggregate,
        filterby=resources
    )

    kwargs['scenario_combos'] = list(product(*selected_scenarios))

    if run_name == 'development':
        results_path = DEV_RESULTS_PATH
    else:
        results_path = os.path.join(PROD_RESULTS_PATH, run_name)

    kwargs['calibration'] = calibration

    if calibration:
        forcings = ['Livneh']
    else:
        # rcp = 'rcp85'
        forcings = list(product(climates, rcps))
        if not forcings:
            return "Please select at least one climate and rcp"

    if consolidate and resample == 'Y':
        return 'Sorry, you cannot consolidate annually resampled data.'

    if tab == 'reservoir-storage':
        attr = 'storage'
        df_storage = load_timeseries(results_path, basin, forcings, 'Reservoir', 'Storage',
                                     multiplier=MCM_TO_TAF, **load_data_kwargs)
        kwargs.pop('transform', None)
        if resample:
            obs = df_obs_storage.resample(resample).mean()
        else:
            obs = df_obs_storage
        for res in get_resources(df_storage, filterby=aggregate or resources):
            component = timeseries_component(attr, res, df_storage, obs, **kwargs)
            children.append(component)

    else:
        df_hp_flow = None
        # df_obs = df_obs_streamflow.loc[df_hydropower.index]
        if resample:
            obs = df_obs_streamflow.resample(resample).mean()
        else:
            obs = df_obs_streamflow

        if tab in ['hydropower-generation', 'hydropower-flow', 'system']:
            hp = []
            df_hp1 = None
            df_hp2 = None

            try:
                df_hp1 = load_timeseries(results_path, basin, forcings, 'PiecewiseHydropower', 'Flow',
                                         **load_data_kwargs) * MCM_TO_CFS
            except:
                pass
            if df_hp1 is not None:
                hp.append(df_hp1)

            try:
                df_hp2 = load_timeseries(results_path, basin, forcings, 'Hydropower', 'Flow',
                                         **load_data_kwargs) * MCM_TO_CFS
            except:
                pass
            if df_hp2 is not None:
                hp.append(df_hp2)
            if hp:
                df_hp_flow = pd.concat(hp, axis=1)

            if aggregate and df_hp_flow is not None:
                df_hp_flow = agg_by_resources(df_hp_flow, aggregate)

        if tab in ['hydropower-generation', 'system']:
            path = '../data/{} River/fixed_head.csv'.format(basin.title())
            if os.path.exists(path):
                fixed_head = pd.read_csv(path, index_col=0, squeeze=True).to_dict()
            else:
                fixed_head = {}

        if tab == 'hydropower-flow':
            attr = 'flow'
            if df_hp_flow is not None:
                for res in get_resources(df_hp_flow, filterby=aggregate or resources):
                    component = timeseries_component(attr, res, df_hp_flow, obs, **kwargs)
                    children.append(component)

        elif tab == 'hydropower-generation':
            attr = 'generation'
            if df_hp_flow is not None:
                for res in get_resources(df_hp_flow, filterby=resources):
                    if res not in fixed_head:
                        continue  # TODO: update to include non-fixed head
                    head = fixed_head[res]
                    component = timeseries_component(attr, res, df_hp_flow, obs, head=head, **kwargs)
                    children.append(component)

        elif tab == 'outflow':
            attr = 'flow'
            df = load_timeseries(results_path, basin, forcings, 'Output', 'Flow',
                                 multiplier=MCM_TO_CFS, **load_data_kwargs)
            for res in get_resources(df, filterby=resources):
                component = timeseries_component(attr, res, df, obs, **kwargs)
                children.append(component)

        # elif tab == 'ifr-flow':
        #     attr = 'flow'
        #     df = load_timeseries(results_path, basin, forcings, 'InstreamFlowRequirement', 'Flow',
        #                          multiplier=MCM_TO_CFS, **load_data_kwargs)
        #     reqt = load_timeseries(results_path, basin, forcings, 'InstreamFlowRequirement', 'Requirement',
        #                            multiplier=MCM_TO_CFS, **load_data_kwargs)
        #     for res in get_resources(df, filterby=resources):
        #         component = timeseries_component(attr, res, df, obs, min_reqt=reqt, **kwargs)
        #         children.append(component)

        elif tab == 'ifr-flow':
            attr = 'flow'
            if basin == 'stn':
                pywr_param_name = 'PiecewiseInstreamFlowRequirement'
            else:
                pywr_param_name = 'InstreamFlowRequirement'
            df = load_timeseries(results_path, basin, forcings, pywr_param_name, 'Flow',
                                 multiplier=MCM_TO_CFS, **load_data_kwargs)
            df_pw_min_ifr_reqt = load_timeseries(
                results_path, basin, forcings, pywr_param_name, 'Min Requirement',
                multiplier=MCM_TO_CFS, **load_data_kwargs)
            df_pw_ifr_range_reqt = load_timeseries(
                results_path, basin, forcings, pywr_param_name, 'Max Requirement',
                multiplier=MCM_TO_CFS, **load_data_kwargs)

            if df_pw_min_ifr_reqt is not None and df_pw_ifr_range_reqt is not None:
                df_pw_max_ifr_reqt = df_pw_min_ifr_reqt[df_pw_ifr_range_reqt.columns] + df_pw_ifr_range_reqt
            else:
                df_pw_max_ifr_reqt = None

            for res in get_resources(df, filterby=resources):
                component = timeseries_component(
                    attr, res, df, obs,
                    min_reqt=df_pw_min_ifr_reqt,
                    max_reqt=df_pw_max_ifr_reqt,
                    **kwargs
                )
                children.append(component)

        elif tab == 'system':

            # System generation
            system_res = 'System generation'
            if df_hp_flow is not None:
                gauged_hp = [c for c in df_hp_flow.columns if gauge_lookup.get(c) in obs]
                gauge_lookup[system_res] = system_res

                df_sim_scenarios = []
                df_obs = []
                df_sim_system = None
                df_obs_system = None
                for i, forcing in enumerate(forcings):
                    dfs_sim = []
                    for res in get_resources(df_hp_flow):
                        head = fixed_head.get(res)
                        hp_gauge = gauge_lookup.get(res)
                        if not head or not hp_gauge:
                            continue
                        sim_energy = flow_to_energy(df_hp_flow[forcing, res], head)
                        dfs_sim.append(sim_energy)
                        if i == 0:
                            obs_energy = flow_to_energy(obs[hp_gauge], head)
                            df_obs.append(obs_energy)
                    if dfs_sim:
                        concatenated_summed = pd.concat(dfs_sim, axis=1).dropna().sum(axis=1)
                        df_sim_scenarios.append(concatenated_summed)
                if df_sim_scenarios:
                    df_sim_system = pd.concat(df_sim_scenarios, axis=1, keys=forcings)
                    df_sim_system.columns = pd.MultiIndex.from_product([forcings, (system_res,)])

                if df_obs:
                    df_obs_system = pd.concat(df_obs, axis=1).sum(axis=1).to_frame(system_res)

                if df_sim_system is not None:
                    hp_component = timeseries_component('generation', system_res, df_sim_system, df_obs_system,
                                                        **kwargs)
                    children.append(hp_component)

    return html.Div(
        children=children,
        className="timeseries-collection"
    )


BODY_STYLE = {
    'display': 'flex'
}

SIDEBAR_STYLE = {
    # "position": "fixed",
    # "top": 50,
    # "left": 0,
    # "bottom": 0,
    "width": "10rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    # "margin-left": "5rem",
    # "margin-right": "2rem",
    "padding": "2rem 1rem",
}

body = html.Div(
    id='app-body',
    style=BODY_STYLE,
    children=[
        dbc.Nav(
            id="sidebar-tabs",
            className="sidebar-content",
            vertical=True,
            pills=True,
            style=SIDEBAR_STYLE,
            children=[
                # dbc.NavItem(dbc.NavLink('Map', href='/map', id='map-tab')),
                # dbc.NavItem(dbc.NavLink('Diagnostics', href='/development', id='development-tab')),
                # # dbc.NavItem(dbc.NavLink('Gauges', href='/gauges', id='gauges-tab')),
                # dbc.NavItem(dbc.NavLink('Analysis', href='/scenarios', id='scenarios-tab')),
            ]),
        html.Div(
            className='main-content',
            id='main-content',
            style=CONTENT_STYLE
        )
    ])

app.title = 'SJ Dashboard'
app.layout = html.Div(
    id="root",
    children=[
        dcc.Store(id='session-store', storage_type='session'),
        dcc.Location(id="url"),
        navbar,
        body
    ])


@app.callback(Output('tabs-content', 'children'),
              [Input('select-basin', 'value')])
def render_basin_tabs_content(basin):
    return [
        html.Div(
            id='{}-tabs-content'.format(basin),
            style={'padding': '10px'},
        )
    ]


@app.callback(Output('scenario-selections', 'children'), [
    Input('select-basin', 'value')
])
def render_scenario_selections(basin):
    if not basin:
        return []

    children = []
    for scenario in SCENARIOS.get(basin, []):
        scenario_name = scenario['name']
        ensembles = ENSEMBLE_NAMES.get(basin, {}).get(scenario_name, range(scenario['size']))
        dropdown = dcc.Dropdown(
            id=scenario_name.replace(' ', '-'),
            options=[{'label': ensemble, 'value': ensemble} for ensemble in ensembles],
            multi=True,
            value=[str(i) for i in ensembles],
            placeholder='Select a {} scenario'.format(scenario_name)
        )
        selector = html.Div([
            html.P([scenario_name]),
            dropdown,
        ], className='scenario-selection')
        children.append(selector)
    return children


@app.callback(Output("select-basin", "options"), [
    Input("select-basins-global", "value")
])
def render_select_development_basin_options(basins):
    return [{"label": BASINS[basin], "value": basin} for basin in basins]


@app.callback(Output("select-basin", "value"), [
    Input("select-basins-global", "value")
])
def render_select_development_basin_value(basins):
    return basins[0]


@app.callback(Output("sidebar-tabs", "children"), [Input("url", "pathname")])
def render_sidebar_tabs(pathname):
    SIDEBAR_TABS = [
        {
            'label': 'Map',
            'href': '/map',
            'id': 'map-tab'
        },
        {
            'label': 'Development',
            'href': '/development',
            'id': 'development-tab'
        },
        {
            'label': 'Scenarios',
            'href': '/scenarios',
            'id': 'scenarios-tab'
        },
        {
            'label': 'Inter-basin trade-offs',
            'href': '/interbasin',
            'id': 'interbasin-tab'
        }
    ]

    nav_items = []
    for t in SIDEBAR_TABS:
        nav_item = dbc.NavItem(
            dbc.NavLink(
                t['label'],
                href=t['href'],
                id=t['id'],
                active=pathname and t['href'] in pathname
            )
        )
        nav_items.append(nav_item)
    return nav_items


# @app.callback(Output('select-themes', 'children'), [
#     Input('select-theme', 'value')
# ])
# def render_theme_selector(selected):
#     return []


@app.callback(Output("main-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == '/':
        return dbc.Jumbotron(
            [
                html.H1("Welcome!"),
                html.Hr(),
                html.P("Select a tab..."),
            ]
        )
    elif pathname == '/map':
        return map_content()
    elif pathname == "/development":
        return development_content('development')
    elif pathname == "/gauges":
        return gauges_content()
    elif pathname == '/scenarios':
        return development_content('scenarios')
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


def map_content():
    return html.Div([
        html.Div(
            [
                dbc.Checklist(
                    id="show-map-labels",
                    options=[
                        {"id": "show-all-labels", "label": "Show labels", "value": "show-all-labels"}
                    ],
                    value=["show-all-labels"],
                )
            ]
        ),
        html.Div(
            id='map-content',
            children=[]
        )
    ], style={"width": "100%"})


@app.callback(Output('map-content', 'children'), [
    Input('show-map-labels', 'value')
])
def render_map(show_labels):
    show_labels = 'show-all-labels' in show_labels
    with open('./Stanislaus River.json') as f:
        oa_network = json.load(f)
    with open('../stanislaus/pywr_model_Livneh_simplified.json') as f:
        pywr_network = json.load(f)

    nodes = [(n['x'], n['y'], n['name']) for n in oa_network['network']['nodes']]
    lons, lats, names = list(zip(*nodes))

    traces = [
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=names,
        )
    ]

    token = open('./secrets/mapbox-token.txt').read()

    layout = dict(
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=37,
                lon=-120
            ),
            pitch=0,
            zoom=5
        ),
        margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
    )

    return [
        dcc.Graph(
            id='mapbox-map',
            className='project-map',
            figure={
                'data': traces,
                'layout': layout,
            },

        )
    ]


@app.callback(Output('percentiles-options', 'options'), [
    Input('percentiles-checklist', 'value')
])
def toggle_percentile_checkboxes(values):
    disabled = 'consolidate' not in values
    if disabled:
        return []
    else:
        return [
            {"id": "percentiles-mean", "label": "Mean", "value": "mean", "disabled": disabled},
            {"id": "percentiles-median", "label": "Median", "value": "median", "disabled": disabled},
            {"id": "percentiles-quartiles", "label": "Quartiles", "value": "quartiles", "disabled": disabled},
            {"id": "percentiles-range", "label": "Range", "value": "range", "disabled": disabled}
        ]


@app.callback(Output('percentiles-type', 'options'), [
    Input('percentiles-checklist', 'value')
])
def toggle_percentile_checkboxes(values):
    disabled = 'consolidate' not in values
    if disabled:
        return []
    else:
        return [
            {"id": "percentiles-timeseries", "label": "Timeseries", "value": "timeseries", "disabled": disabled},
            {"id": "percentiles-boxplots", "label": "Boxplots", "value": "boxplots", "disabled": disabled},
        ]


@app.callback(
    Output('select-resources', 'value'),
    [
        # Input('url', 'pathname'),
        Input('select-basin', 'value'),
        Input('development-tabs', 'active_tab')
    ],
    [State('session-store', 'data')]
)
def update_selected_resources(basin, tab, data):
    # scope = pathname.split('/')[1]
    data = data or {}
    # scope_data = data.get(scope, {})
    if not basin:
        return []
    tab_data = data.get((tab, basin), {})
    return tab_data.get('resources', [])


@app.callback(
    Output('session-store', 'data'),
    [
        # Input('url', 'pathname'),
        Input('development-tabs', 'active_tab'),
        Input('select-resources', 'value')
    ],
    [State('session-store', 'data')]
)
def store_selected_resources(tab, resources, data):
    data = data or {}
    # scope = pathname.split('/')[1]
    # scoped_data = data.get(scope, {})
    tab_data = data.get(tab, {})
    tab_data['resources'] = resources
    # scoped_data[tab] = tab_data
    data[tab] = tab_data
    return data


@app.callback(Output('select-resources', 'options'), [
    Input('development-tabs', 'active_tab'),
    Input('select-basin', 'value')
])
def update_select_resources(tab, basin):
    res_options = RES_OPTIONS.get(basin, {})
    options = []
    if tab == 'reservoir-storage':
        options = res_options.get(('Reservoir', 'storage'))
    elif tab in ['hydropower-flow', 'hydropower-generation']:
        opts_npw = res_options.get(('Hydropower', 'flow'), [])
        opts_pw = res_options.get(('PiecewiseHydropower', 'flow'), [])
        options = opts_npw + opts_pw
    elif tab == 'outflow':
        options = res_options.get(('Output', 'flow'))
    elif tab == 'ifr-flow':
        options = res_options.get(('InstreamFlowRequirement', 'flow'))
    # elif tab == 'ifr-range-flow':
    #     options = res_options.get(('PiecewiseInstreamFlowRequirement', 'flow'))

    return options or []


@app.callback(Output('development-tabs-content', 'children'),
              [
                  Input('development-tabs', 'active_tab'),
                  Input('select-basin', 'value'),
                  Input('radio-transform', 'value'),
                  Input('radio-resample', 'value'),
                  Input('radio-aggregate', 'value'),
                  Input('percentiles-checklist', 'value'),
                  Input('percentiles-options', 'value'),
                  Input('percentiles-type', 'value'),
                  Input('select-resources', 'value'),
                  Input('reload', 'n_clicks'),
              ])
def render_development_content(tab, basin, transform, resample, aggregate, consolidate, percentiles, percentiles_type,
                               resources,
                               n_clicks):
    kwargs = dict(
        basin=basin,
        resources=resources,
        transform=transform,
        resample=resample,
        aggregate=aggregate,
        consolidate=consolidate,
        percentiles=percentiles,
        percentiles_type=percentiles_type,
        run_name='development'
    )
    return render_timeseries_collection(tab, **kwargs)


if __name__ == '__main__':
    app.run_server(debug=False)
