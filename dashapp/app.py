# -*- coding: utf-8 -*-
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objs as go

import dash_daq as daq

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

opath = '../data/{basin}/gauges/{attr}.csv'
PATH_TEMPLATES = {
    'mcm': '../results/{basin}/with optimization/{scenario}/{res_type}_{res_attr}_mcm.csv',
    'Variable Head': '../results/{basin}/with optimization/{scenario}/{res_type}_{res_attr}_m.csv',
}

basin = 'stanislaus'

MCM_TO_CFS = 1e6 / 24 / 3600 * 35.31
MCM_TO_TAF = 1.2335

AXIS_LABELS = {
    'storage': 'Storage (TAF)',
    'flow': 'Flow (cfs)',
    'generation': 'Generation (MWh)'
}

PLOTLY_CONFIG = {
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['toggleSpikelines', 'sendDataToCloud', 'autoScale2d', 'zoomOut2d', 'zoomIn2d',
                               'editInChartStudio', 'boxSelect',
                               'lassoSelect'],
    'showLink': False,
}

source_text = {'simulated': 'Simulated', 'observed': 'Observed'}
# source_name = {'simulated': 'Simulated'}
source_color = {'simulated': 'blue', 'observed': 'darkgrey'}


def flow_to_energy(df, head):
    return df * head * 0.9 * 9.81 * 1000 / 1e6


def get_plot_kwargs(source):
    return dict(
        text=source_text[source],
        mode='lines',
        opacity=0.7,
        name=source_text[source],
        line=go.scatter.Line(color=source_color[source])
    )


df_obs_storage = pd.read_csv(
    opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='storage'),
    index_col=[0],
    parse_dates=True
) * MCM_TO_TAF

# df_obs_streamflow = pd.read_csv(
#     opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='streamflow'),
#     index_col=[0],
#     parse_dates=True
# ).loc[df_hydropower.index].ffill() * MCM_TO_CFS  # mcm to cfs

df_obs_streamflow = pd.read_csv(
    opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='streamflow_cfs'),
    index_col=[0],
    parse_dates=True
).ffill()

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


def load_timeseries(basin, scenario, res_type, res_attr, tpl='mcm'):
    path_tpl = PATH_TEMPLATES[tpl]
    return pd.read_csv(
        path_tpl.format(basin=basin, scenario=scenario, res_type=res_type, res_attr=res_attr),
        index_col=[0],
        parse_dates=True,
    )


def consolidate_dataframe(df, resample):
    if not resample:
        fmt = '%j'
    else:
        fmt = '%m'
    new_index = [(date.strftime(fmt), str(date.year)) for date in df.index]

    df.index = pd.MultiIndex.from_tuples(new_index)
    df = df.unstack(level=-1)
    return df


percentile_colors = {
    'simulated': 'blue',
    'observed': 'grey'
}


def percentile_graphs(df, source):
    percentiles = [0.25, 0.5, 0.75]
    lines = []
    for q in percentiles:
        opacity = 0.1
        fill = None
        if 0.25 < q <= 0.75:
            opacity = 0.75
        if q > percentiles[0]:
            fill = 'tonexty'
        lines.append(
            go.Scatter(
                x=df.index,
                y=df.quantile(q, axis=1),
                mode='lines',
                fill=fill,
                opacity=opacity,
                text='{}{}'.format(source.title()[0], q),
                name='{}. {}'.format(source.title()[:3], q),
                line_color=percentile_colors[source]
            )
        )

    return lines


def timeseries_component(attr, res_name, sim_vals, df_obs, **kwargs):
    res_name_id = res_name.lower().replace(' ', '_')
    ts_data = []
    fd_data = []

    resample = kwargs.get('resample')
    consolidate = kwargs.get('consolidate')

    if resample:
        sim_resampled = sim_vals.resample(resample).mean()
    else:
        sim_resampled = sim_vals

    plot_max = False
    max_reqt = kwargs.get('max_reqt')
    if max_reqt is not None and res_name in max_reqt:
        plot_max = True

    min_reqt = kwargs.get('min_reqt')
    if not consolidate and min_reqt is not None and res_name in min_reqt:
        ts_data.append(
            go.Scatter(
                x=min_reqt.index,
                y=min_reqt[res_name],
                text='Min Requirement',
                mode='lines',
                opacity=0.7,
                # opacity=0.7 if not plot_max else 0.0,
                name='Min Requirement',
                line_color='red'
            )
        )

    if not consolidate and plot_max:
        ts_data.append(
            go.Scatter(
                x=max_reqt.index,
                y=max_reqt[res_name],
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
        sim_cons = consolidate_dataframe(sim_resampled, resample)
        sim_vals = sim_cons.quantile(0.5, axis=1)
        sim_data = percentile_graphs(sim_cons, 'simulated')
        ts_data.extend(sim_data)

    else:
        ts_data.append(
            go.Scatter(
                x=sim_resampled.index,
                y=sim_resampled,
                text='Simulated',
                mode='lines',
                opacity=0.7,
                name='Simulated',
                line=go.scatter.Line(color='blue')
            )
        )

    N = len(sim_resampled)
    fd_data.append(
        go.Scatter(
            x=sorted(sim_resampled.values),
            y=np.arange(0, N) / N * 100,
            **get_plot_kwargs('simulated')
        )
    )

    gauges = []
    gauge_name = gauge_lookup.get(res_name, res_name)
    pbias = 100
    nse = -1

    if gauge_name in df_obs:
        obs_vals = df_obs[gauge_name]

        head = kwargs.get('head')
        if head:
            obs_vals = flow_to_energy(obs_vals, head)

        if not consolidate:  # consolidated values will use the whole record
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
        fd_data.append(
            go.Scatter(
                x=sorted(obs_vals.values),
                y=np.arange(0, N) / N * 100,
                **get_plot_kwargs('observed')
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
            obs_data = percentile_graphs(obs_cons, 'observed')
            ts_data.extend(obs_data)
        else:
            obs_graph = go.Scatter(
                x=obs_resampled.index,
                y=obs_resampled,
                **get_plot_kwargs('observed')
            )
            ts_data.insert(0, obs_graph)

    if nse <= 0:
        nse_color = 'red'
    elif nse <= 0.5:
        nse_color = 'orange'
    else:
        nse_color = 'green'

    nse_gauge = daq.Gauge(
        id='nse-gauge-' + res_name_id,
        label='NSE',
        size=120,
        min=-1.0,
        value=nse,
        max=1.0,
        color=nse_color,
    )

    if abs(pbias) >= 20:
        pbias_color = 'red'
    elif abs(pbias) >= 10:
        pbias_color = 'orange'
    else:
        pbias_color = 'green'

    pbias_gauge = daq.Gauge(
        id='pbias-gauge-' + res_name_id,
        label='% bias',
        size=120,
        min=min(pbias, -100.0),
        value=pbias,
        max=max(pbias, 100.0),
        color=pbias_color
    )

    gauges = [nse_gauge, pbias_gauge]

    ylabel = AXIS_LABELS.get(attr, 'unknown')

    timeseries_graph = dcc.Graph(
        id='timeseries-' + res_name_id,
        className='timeseries-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': ts_data,
            'layout': go.Layout(
                title='Timeseries',
                xaxis={'title': 'Date'},
                yaxis={'title': ylabel, 'rangemode': 'tozero'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
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
                yaxis={'title': 'Duration (%)'},
                xaxis={'title': ylabel},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                xaxis_type=kwargs.get('transform', 'linear')
            )
        },
    )

    children = [timeseries_graph, flow_duration_graph] + gauges

    div = html.Div(
        children=[
            html.H5(res_name),
            html.Div(
                children=children,
                className="timeseries-metrics-data"
            )
        ],
        className="timeseries-metrics-box"
    )

    return div


def gauges_component(**kwargs):
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


navbar = dbc.NavbarSimple(
    children=[
        # dbc.NavItem(dbc.NavLink("Link", href="#")),
        # dbc.DropdownMenu(
        #     nav=True,
        #     in_navbar=True,
        #     label="Menu",
        #     children=[
        #         dbc.DropdownMenuItem("Entry 1"),
        #         dbc.DropdownMenuItem("Entry 2"),
        #         dbc.DropdownMenuItem(divider=True),
        #         dbc.DropdownMenuItem("Entry 3"),
        #     ],
        # ),
    ],
    brand="San Joaquin Dashboard",
    brand_href="#",
    # sticky="top",
)

transform_form = dbc.FormGroup(
    [
        dbc.Label("Transform", html_for="radio-transform", width=2),
        dbc.RadioItems(
            id="radio-transform",
            options=[
                {"label": "Linear", "value": 'linear'},
                {"label": "Log", "value": 'log'},
            ],
            value='linear',
            inline=True
        ),
    ],
)

resample_form = dbc.FormGroup(
    [
        dbc.Label("Resampling", html_for="radio-resample", width=2),
        dbc.RadioItems(
            id="radio-resample",
            options=[
                {"label": "None", "value": None},
                {"label": "Monthly", "value": 'M'},
                {"label": "Annual", "value": 'Y'},
            ],
            value=None,
            inline=True
        ),
    ],
)

consolidation_form = dbc.FormGroup(
    [
        dbc.Checklist(
            id="toggle-consolidate",
            options=[
                {"label": "Percentiles", "value": "consolidate"}
            ],
            value=[],
        ),
    ],
)


def timeseries_content():
    return html.Div(children=[
        # html.H1(children='Model diagnostics'),
        dbc.Form(
            [
                transform_form,
                resample_form,
                consolidation_form
            ],
            inline=True
        ),

        dbc.Tabs(id="timeseries-tabs", active_tab='reservoir-storage', children=[
            dbc.Tab(label='Reservoir storage', tab_id='reservoir-storage'),
            dbc.Tab(label='PH flow', tab_id='hydropower-flow'),
            dbc.Tab(label='PH generation', tab_id='hydropower-generation'),
            dbc.Tab(label='IFR flow (min)', tab_id='ifr-flow'),
            dbc.Tab(label='IFR flow (range)', tab_id='ifr-range-flow'),
            dbc.Tab(label='Outflow', tab_id='outflow'),
            dbc.Tab(label='System', tab_id='system'),
        ]),
        html.Div(
            id='timeseries-tabs-content',
            style={'padding': '10px'},
        )
    ])


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
                dbc.NavItem(dbc.NavLink('Timeseries', href='/timeseries', id='timeseries-tab')),
                dbc.NavItem(dbc.NavLink('Gauges', href='/gauges', id='gauges-tab')),
            ]),
        html.Div(
            className='main-content',
            id='main-content',
            style=CONTENT_STYLE
        )
    ])

app.title = 'SJ Dashboard'
app.layout = html.Div([dcc.Location(id="url"), navbar, body])


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
    elif pathname == "/timeseries":
        return timeseries_content()
    elif pathname == "/gauges":
        return gauges_component()
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(Output('timeseries-tabs-content', 'children'),
              [
                  Input('timeseries-tabs', 'active_tab'),
                  Input('radio-transform', 'value'),
                  Input('radio-resample', 'value'),
                  Input('toggle-consolidate', 'value')
              ])
def render_timeseries_content(tab, transform, resample, consolidated):
    children = []
    consolidate = "consolidate" in consolidated
    scenario = 'Livneh'

    kwargs = dict(transform=transform, consolidate=consolidate, resample=resample)

    if consolidate and resample == 'Y':
        return 'Sorry, you cannot consolidate annually resampled data.'

    if tab == 'reservoir-storage':
        attr = 'storage'
        df_storage = load_timeseries(basin, scenario, 'Storage', 'Storage') * MCM_TO_TAF
        kwargs.pop('transform', None)
        if resample:
            obs = df_obs_storage.resample(resample).mean()
        else:
            obs = df_obs_storage
        for res in sorted(df_storage.columns):
            component = timeseries_component(attr, res, df_storage[res], obs, **kwargs)
            children.append(component)

    else:
        # df_obs = df_obs_streamflow.loc[df_hydropower.index]
        if resample:
            obs = df_obs_streamflow.resample(resample).mean()
        else:
            obs = df_obs_streamflow

    if tab in ['hydropower-generation', 'hydropower-flow', 'system']:
        df_hp1 = load_timeseries(basin, scenario, 'PiecewiseHydropower', 'Flow')
        df_hp2 = load_timeseries(basin, scenario, 'Hydropower', 'Flow')
        df_hp_flow = pd.concat([df_hp1, df_hp2], axis=1) * MCM_TO_CFS  # mcm to cfs

    if tab in ['hydropower-generatoin', 'system']:
        fixed_head = pd.read_csv('../data/{} River/fixed_head.csv'.format(basin.title()), index_col=0,
                                 squeeze=True).to_dict()

    if tab == 'hydropower-generation':
        attr = 'generation'
        for res in sorted(df_hp_flow.columns):
            if res not in fixed_head:
                continue
            head = fixed_head[res]
            df_gen = flow_to_energy(df_hp_flow[res], head)
            component = timeseries_component(attr, res, df_gen, obs, head=head, **kwargs)
            children.append(component)

    elif tab == 'outflow':
        attr = 'flow'
        df_outflow = load_timeseries(basin, scenario, 'Output', 'Outflow') * MCM_TO_CFS
        for res in sorted(df_outflow.columns):
            component = timeseries_component(attr, res, df_outflow[res], obs, **kwargs)
            children.append(component)

    elif tab == 'hydropower-flow':
        attr = 'flow'
        df = df_hp_flow
        for res in sorted(df.columns):
            component = timeseries_component(attr, res, df[res], obs, **kwargs)
            children.append(component)

    elif tab == 'ifr-flow':
        attr = 'flow'
        df = load_timeseries(basin, scenario, 'InstreamFlowRequirement', 'Flow') * MCM_TO_CFS
        reqt = load_timeseries(basin, scenario, 'InstreamFlowRequirement', 'Requirement') * MCM_TO_CFS
        for res in sorted(df.columns):
            component = timeseries_component(
                attr, res, df[res], obs,
                min_reqt=reqt,
                **kwargs
            )
            children.append(component)

    elif tab == 'ifr-range-flow':
        attr = 'flow'
        df = load_timeseries(basin, scenario, 'PiecewiseInstreamFlowRequirement', 'Flow') * MCM_TO_CFS  # mcm to cfs
        df_pw_min_ifr_reqt = load_timeseries(basin, scenario, 'PiecewiseInstreamFlowRequirement',
                                             'Min Requirement') * MCM_TO_CFS  # mcm to cfs
        df_pw_ifr_range_reqt = load_timeseries(basin, scenario, 'PiecewiseInstreamFlowRequirement',
                                               'Max Requirement') * MCM_TO_CFS  # mcm to cfs

        df_pw_max_ifr_reqt = df_pw_min_ifr_reqt[df_pw_ifr_range_reqt.columns] + df_pw_ifr_range_reqt

        for res in sorted(df.columns):
            component = timeseries_component(
                attr, res, df[res], obs,
                min_reqt=df_pw_min_ifr_reqt,
                max_reqt=df_pw_max_ifr_reqt,
                **kwargs
            )
            children.append(component)

    elif tab == 'system':

        # System generation
        res = 'System generation'
        gauged_hp = [c for c in df_hp_flow.columns if gauge_lookup.get(c) in obs]
        hp_gauges = [gauge_lookup[c] for c in gauged_hp]
        gauge_lookup[res] = res

        df_sim = []
        df_obs = []
        for hp in df_hp_flow.columns:
            head = fixed_head.get(hp)
            hp_gauge = gauge_lookup.get(hp)
            if not head or not hp_gauge:
                continue
            df_sim.append(flow_to_energy(df_hp_flow[hp], head))
            df_obs.append(flow_to_energy(obs[hp_gauge], head))
        df_sim_system = pd.concat(df_sim, axis=1).sum(axis=1)  # should be series?
        df_obs_system = pd.concat(df_obs, axis=1).sum(axis=1).to_frame(res)
        hp_component = timeseries_component('generation', res, df_sim_system, df_obs_system, **kwargs)
        children.append(hp_component)

    return html.Div(
        children=children,
        className="timeseries-collection"
    )


if __name__ == '__main__':
    app.run_server(debug=False)
