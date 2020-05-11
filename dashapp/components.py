from itertools import product
import os

import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html

from dashapp.metrics import nash_sutcliffe_efficiency, percent_bias, root_mean_square_error
from dashapp.functions import get_resources, flow_to_energy, consolidate_dataframe, load_timeseries, agg_by_resources
from dashapp.constants import PLOTLY_CONFIG, ABS_DIFF, PCT_DIFF, MCM_TO_CFS, MCM_TO_TAF, PROD_RESULTS_PATH, \
    DEV_RESULTS_PATH, BASINS

MULTIPLIERS = {
    'storage': MCM_TO_TAF,
    'flow': MCM_TO_CFS,
    'requirement': MCM_TO_CFS,
    'elevation': 1.0
}

OBSERVED_TEXT = 'Observed'
OBSERVED_COLOR = 'lightgrey'

AXIS_LABELS = {
    'storage': 'Storage (TAF)',
    'flow': 'Flow (cfs)',
    'requirement': 'Flow (cfs)',
    'generation': 'Generation (MWh)',
    'M': 'Month',
    'Y': 'Year'
}

PALETTES = {
    'P2009': 'Blues_r',
    'P2030': 'BuGn_r',
    'P2060': 'OrRd_r'
}

FLOOD_CONTROL_RESERVOIRS = ['New Melones Lake', 'Lake Tulloch', 'Don Pedro Reservoir', 'Millerton Lake']

percentiles_ordered = {
    ('median', 'quartiles'): ['quartiles', 'median'],
    ('median', 'quartiles', 'range'): ['range', 'quartiles', 'median'],
    ('quartiles', 'range'): ['range', 'quartiles'],
    ('median', 'range'): ['range', 'median']
}


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


def timeseries_component(attr, res_name, all_sim_vals, df_obs, **kwargs):
    res_name_id = res_name.lower().replace(' ', '_')
    ts_data = []
    fd_data = []

    gauge_lookup = kwargs.get('gauge_lookup')
    metric = kwargs.get('metric')
    metric = metric != 'default' and metric
    resample = kwargs.get('resample')
    constraints = kwargs.get('constraints', [])
    percentiles = kwargs.get('percentiles')
    consolidate = kwargs.get('consolidate')
    calibration = kwargs.get('calibration')
    climates = kwargs.get('climates')
    rcps = kwargs.get('rcps')
    percentiles_type = kwargs.get('percentiles_type', 'timeseries')
    scenario_combos = kwargs.get('scenario_combos', [])
    head = kwargs.get('head')
    layout = kwargs.get('layout_options', [])
    compact = kwargs.get('compact', False)
    show_fd = 'flow-duration' in layout and not compact
    show_fc = 'guide' in constraints
    color_idx = -1

    # Variables for observed data
    obs_vals = None
    gauges = []
    gauge_name = gauge_lookup.get(res_name, res_name)

    fc_df = None
    if attr == 'storage' and show_fc and res_name in FLOOD_CONTROL_RESERVOIRS:
        basin = kwargs.get('basin')
        basin_full_name = '{} River'.format(BASINS[basin])
        data_path = os.environ['SIERRA_DATA_PATH']
        filename = '{} Flood Control Curve mcm.csv'.format(res_name)
        fcpath = os.path.join(data_path, basin_full_name, 'management', 'BAU', 'Flood Control', filename)
        flood_control_curve = pd.read_csv(fcpath, index_col=0, header=0).iloc[:, 0] / 1.2335  # mcm to TAF
        fc_df = pd.DataFrame(index=all_sim_vals.index)
        fc_df['Rainflood space'] = fc_df.index.strftime('%#m-%#d')
        fc_df.replace({'Rainflood space': flood_control_curve}, inplace=True)

        ts_data.append(
            go.Scatter(
                x=fc_df.index,
                y=fc_df['Rainflood space'],
                text='Flood Curve',
                mode='lines',
                opacity=0.7,
                # opacity=0.7 if not plot_max else 0.0,
                name='Flood Curve',
                line_color='red'
            )
        )

    for i, forcing in enumerate(set(all_sim_vals.columns.get_level_values(0))):
        parts = forcing.split('/')[1].split('_')
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
        for i, scenario_combo in enumerate(scenario_combos):

            color_idx += 1
            sim_color = sns.color_palette().as_hex()[color_idx]

            if scenario_combo:
                scenario_name = '{} {}'.format(tuple(parts), scenario_combo)
            else:
                scenario_name = '-'.join(tuple(parts))

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

            # Prepare observed data
            if i == 0:
                obs_resampled = None
                if calibration and df_obs is not None and gauge_name in df_obs:
                    obs_vals = df_obs[gauge_name]

                    head = kwargs.get('head')
                    if head:
                        obs_vals = flow_to_energy(obs_vals, head)

                    if not consolidate:  # percentiles values will use the whole record
                        obs_vals = obs_vals.reindex(sim_vals.index)

                    if resample:
                        obs_resampled = obs_vals.resample(resample, axis=0).mean()
                    else:
                        obs_resampled = obs_vals

                    if consolidate:  # use original values
                        obs_cons = consolidate_dataframe(obs_resampled, resample)
                        obs_vals = obs_cons.quantile(0.5, axis=1)  # for use in flow-duration curve

            if metric == ABS_DIFF:
                sim_resampled -= obs_resampled
            elif metric == PCT_DIFF:
                sim_resampled = (sim_resampled / obs_resampled - 1.0) * 100.0

            plot_max = False
            max_reqt = kwargs.get('max_reqt')
            if max_reqt is not None and res_name in max_reqt[forcing] and 'max' in constraints:
                plot_max = True

            # Minimum flow requirement
            min_reqt = kwargs.get('min_reqt')
            show_min_reqt = not consolidate and min_reqt is not None and res_name in min_reqt[
                forcing] and 'min' in constraints
            if show_min_reqt:
                if resample:
                    min_reqt_resampled = min_reqt.resample(resample).mean()
                else:
                    min_reqt_resampled = min_reqt.copy()
                ts_data.append(
                    go.Scatter(
                        x=min_reqt_resampled[forcing].index,
                        y=min_reqt_resampled[forcing][res_name],
                        text='Min Flow',
                        mode='lines',
                        opacity=0.7,
                        # opacity=0.7 if not plot_max else 0.0,
                        name='Min Flow',
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
            if show_fd:
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

    pbias = 100
    nse = -1

    if calibration and obs_resampled is not None and not metric:

        # flow-duration curve
        N = len(obs_resampled)
        if show_fd:
            fd_data.insert(0,
                           go.Scatter(
                               y=sorted(obs_resampled.values),
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
            elif percentiles_type == 'boxplots':
                obs_data = boxplots_graphs(obs_cons, OBSERVED_TEXT, percentiles, color=OBSERVED_COLOR)
            ts_data.extend(obs_data)
        else:
            obs_graph = go.Scatter(
                x=obs_resampled.index,
                y=obs_resampled,
                connectgaps=False,
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

    CLASS_NAME = 'timeseries-chart'
    PLOTLY_CONFIG['displayModeBar'] = not compact and 'toolbar' in layout

    if compact:
        style = {
            'height': 200,
            'width': 400
        }
    elif show_fd:
        style = {
            'height': 300,
            'width': "70%"
        }
    else:
        style = {
            'height': 300,
            'width': "100%"
        }

    layout_kwargs = dict(
        xaxis={'title': AXIS_LABELS.get(resample, "Date"), 'tickangle': -45},
        yaxis={'title': ylabel, 'rangemode': 'tozero'},
        margin={'l': 60, 'b': 80, 't': 40, 'r': 10},
        showlegend=not compact,
        legend={'x': 0.02, 'y': 0.98},
        hovermode='closest',
        yaxis_type=kwargs.get('transform', 'linear'),
    )
    if compact:
        del layout_kwargs['xaxis']['title']
        layout_kwargs['margin'].update(b=60, t=30)
        layout_kwargs['title'] = res_name

    timeseries_graph = dcc.Graph(
        id='timeseries-{}'.format(res_name_id),
        # className=CLASS_NAME,
        style=style,
        config=PLOTLY_CONFIG,
        figure={
            'data': ts_data,
            'layout': go.Layout(
                **layout_kwargs
            ),
        }
    )

    children = [timeseries_graph]

    if show_fd:
        flow_duration_graph = dcc.Graph(
            id='flow-duration-' + res_name_id,
            className='flow-duration-chart',
            config=PLOTLY_CONFIG,
            figure={
                'data': fd_data,
                'layout': go.Layout(
                    # title='{}-duration'.format(attr.title()),
                    xaxis={'title': 'Duration (%)'},
                    yaxis={'title': ylabel},
                    margin={'l': 60, 'b': 80, 't': 40, 'r': 10},
                    legend={'x': 0.05, 'y': 0.95},
                    hovermode='closest',
                    yaxis_type=kwargs.get('transform', 'linear')
                )
            },
            style={"width": "30%"}
        )
        children.append(flow_duration_graph)

    div = html.Div(
        # key='{}'.format(consolidate),
        children=[
            not compact and html.H5(res_name),
            html.Div(
                children=children,
                className="timeseries-metrics-data",
            )
        ],
        className="timeseries-metrics-box",
        style={
            'margin': 10 if compact else 'initial'
        }
    )

    return div


def timeseries_collection(tab, **kwargs):
    children = []
    resources = kwargs.pop('resources', None)
    basin_scenarios = kwargs.pop('basin_scenarios', {})
    selected_scenarios = kwargs.pop('selected_scenarios', [])
    gauge_lookup = kwargs.get('gauge_lookup')
    df_obs = {
        'flow': kwargs.pop('df_obs_streamflow', None),
        'storage': kwargs.pop('df_obs_storage', None)
    }
    consolidate = "consolidate" in kwargs.get('consolidate', [])
    kwargs['consolidate'] = consolidate
    kwargs['compact'] = compact = 'compact' in kwargs.get('layout_options', [])

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
        nscenarios=max(len(basin_scenarios), 1),
        aggregate=aggregate,
        filterby=resources,
        basin_scenarios=basin_scenarios
    )

    kwargs['scenario_combos'] = list(product(*selected_scenarios))

    if run_name == 'development':
        results_path = DEV_RESULTS_PATH
    else:
        results_path = os.path.join(PROD_RESULTS_PATH, run_name)

    kwargs['calibration'] = calibration

    if calibration:
        forcings = ['historical/Livneh']
    else:
        # rcp = 'rcp85'
        forcings = list(product(climates, rcps))
        if not forcings:
            return "Please select at least one climate and rcp"

    if consolidate and resample == 'Y':
        return 'Sorry, you cannot consolidate annually resampled data.'

    resource_class, attr, unit = tab.split('-')

    if 'storage' in attr:
        kwargs.pop('transform', None)

    load_data_kwargs['multiplier'] = MULTIPLIERS.get(attr, 1.0)

    attr_id = tab
    df = load_timeseries(results_path, basin, forcings, attr_id, **load_data_kwargs)

    obs = None
    if attr in df_obs:
        obs = df_obs[attr].copy()
        if resample:
            obs = obs.resample(resample).mean()

    filtered_resources = get_resources(df, filterby=aggregate or resources)
    for res in filtered_resources:
        component = timeseries_component(attr, res, df, obs, **kwargs)
        children.append(component)

    return html.Div(
        children=children,
        className="timeseries-collection",
        style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'flexDirection': 'column' if not compact else None
        }
    )
