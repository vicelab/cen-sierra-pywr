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
rpath = '../{basin}/results/with optimization/{res_type}_{res_attr}_mcm.csv'
basin = 'stanislaus'

MCM_TO_CFS = 1e6 / 24 / 3600 * 35.31

PLOTLY_CONFIG = {
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['toggleSpikelines', 'sendDataToCloud', 'autoScale2d', 'zoomOut2d', 'zoomIn2d',
                               'editInChartStudio', 'boxSelect',
                               'lassoSelect']
}

source_text = {'simulated': 'Simulated', 'observed': 'Observed'}
# source_name = {'simulated': 'Simulated'}
source_color = {'simulated': 'blue', 'observed': 'darkgrey'}


def get_plot_kwargs(source):
    return dict(
        text=source_text[source],
        mode='lines',
        opacity=0.7,
        name=source_text[source],
        line=go.scatter.Line(color=source_color[source])
    )


df_storage = pd.read_csv(
    rpath.format(basin=basin, res_type='Storage', res_attr='Storage'),
    index_col=[0],
    parse_dates=True
)
df_hp1 = pd.read_csv(
    rpath.format(basin=basin, res_type='PiecewiseHydropower', res_attr='Flow'),
    index_col=[0],
    parse_dates=True,
)

df_hp2 = pd.read_csv(
    rpath.format(basin=basin, res_type='Hydropower', res_attr='Flow'),
    index_col=[0],
    parse_dates=True,
)

df_hydropower = pd.concat([df_hp1, df_hp2], axis=1) * MCM_TO_CFS  # mcm to cfs

df_ifr = pd.read_csv(
    rpath.format(basin=basin, res_type='InstreamFlowRequirement', res_attr='Flow'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_outflow = pd.read_csv(
    rpath.format(basin=basin, res_type='Output', res_attr='Outflow'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_pw_ifr = pd.read_csv(
    rpath.format(basin=basin, res_type='PiecewiseInstreamFlowRequirement', res_attr='Flow'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_ifr_reqt = pd.read_csv(
    rpath.format(basin=basin, res_type='InstreamFlowRequirement', res_attr='Requirement'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_pw_min_ifr_reqt = pd.read_csv(
    rpath.format(basin=basin, res_type='PiecewiseInstreamFlowRequirement', res_attr='Min Requirement'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_pw_ifr_range_reqt = pd.read_csv(
    rpath.format(basin=basin, res_type='PiecewiseInstreamFlowRequirement', res_attr='Max Requirement'),
    index_col=[0],
    parse_dates=True,
) * MCM_TO_CFS  # mcm to cfs

df_pw_max_ifr_reqt = df_pw_min_ifr_reqt[df_pw_ifr_range_reqt.columns] + df_pw_ifr_range_reqt

df_obs_storage = pd.read_csv(
    opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='storage'),
    index_col=[0],
    parse_dates=True
).loc[df_storage.index]

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
    slope, intercept, r_value, p_value, std_err = stats.linregress(predictions, targets)
    return r_value ** 2


def percent_bias(predictions, targets):
    return predictions.mean() / targets.mean() - 1


def timeseries_component(attr, res_name, sim_vals, df_obs, **kwargs):
    res_name_id = res_name.lower().replace(' ', '_')
    ts_data = []
    fd_data = []

    plot_max = False
    max_reqt = kwargs.get('max_reqt')
    if max_reqt is not None and res_name in max_reqt:
        plot_max = True

    min_reqt = kwargs.get('min_reqt')
    if min_reqt is not None and res_name in min_reqt:
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

    if plot_max:
        ts_data.append(
            go.Scatter(
                x=max_reqt.index,
                y=max_reqt[res_name],
                text='Max Requirement',
                mode='lines',
                fill='tonexty',
                opacity=0.7,
                name='Max Requirement',
                line_color='grey',
                line=dict(width=0.5)
            )
        )

    ts_data.append(
        go.Scatter(
            x=sim_vals.index,
            y=sim_vals,
            text='Simulated',
            mode='lines',
            opacity=0.7,
            name='Simulated',
            line=go.scatter.Line(color='blue')
        )
    )

    N = len(sim_vals)
    fd_data.append(
        go.Scatter(
            x=sorted(sim_vals.values),
            y=np.arange(0, N) / N * 100,
            **get_plot_kwargs('simulated')
        )
    )

    gauges = []
    gauge_name = gauge_lookup.get(res_name, res_name)

    if gauge_name not in df_obs:
        obs_vals = np.zeros(len(df_obs))
        pbias = 100
        nse = -1

    else:
        obs_vals = df_obs[gauge_name]

        N = len(obs_vals)
        fd_data.append(
            go.Scatter(
                x=sorted(obs_vals.values),
                y=np.arange(0, N) / N * 100,
                **get_plot_kwargs('observed')
            )
        )

        predictions = sim_vals.values
        targets = obs_vals.loc[sim_vals.index].values

        pbias = percent_bias(predictions, targets) * 100
        rmse = root_mean_square_error(predictions, targets)
        nse = nash_sutcliffe_efficiency(predictions, targets)

    obs_graph = go.Scatter(
        x=df_obs.index,
        y=obs_vals,
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

    if attr == 'storage':
        ylabel = 'Storage (TAF)'
    else:
        ylabel = 'Flow (cfs)'

    timeseries_graph = dcc.Graph(
        id='timeseries-' + res_name_id,
        className='timeseries-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': ts_data,
            'layout': go.Layout(
                title='Timeseries',
                xaxis={'title': 'Date'},
                yaxis={'title': ylabel},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                yaxis_type=kwargs.get('transform')
            )
        }
    )

    flow_duration_graph = dcc.Graph(
        id='flow-duration-' + res_name_id,
        className='flow-duration-chart',
        config=PLOTLY_CONFIG,
        figure={
            'data': fd_data,
            'layout': go.Layout(
                title='Flow-duration',
                yaxis={'title': 'Duration (%)'},
                xaxis={'title': ylabel},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                xaxis_type=kwargs.get('transform')
            )
        }
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
                yaxis={'title': 'Flow'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                yaxis_type=kwargs.get('transform')
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


def timeseries_content():
    return html.Div(children=[
        # html.H1(children='Model diagnostics'),

        dbc.Tabs(id="timeseries-tabs", active_tab='reservoir-storage', children=[
            dbc.Tab(label='Reservoir storage', tab_id='reservoir-storage'),
            dbc.Tab(label='PH flow', tab_id='hydropower-flow'),
            dbc.Tab(label='IFR flow (min)', tab_id='ifr-flow'),
            dbc.Tab(label='IFR flow (range)', tab_id='ifr-range-flow'),
            dbc.Tab(label='Outflow', tab_id='outflow'),
            dbc.Tab(label='System', tab_id='system'),
        ]),
        html.Div(id='timeseries-tabs-content', style={'padding': '10px'})
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
              [Input('timeseries-tabs', 'active_tab')])
def render_timeseries_content(tab):
    children = []

    df_obs = df_obs_streamflow.loc[df_hydropower.index]

    if tab == 'reservoir-storage':
        attr = 'storage'
        for res in sorted(df_storage.columns):
            component = timeseries_component(attr, res, df_storage[res], df_obs_storage)
            children.append(component)

    if tab == 'outflow':
        attr = 'flow'
        for res in sorted(df_outflow.columns):
            component = timeseries_component(attr, res, df_outflow[res], df_obs)
            children.append(component)

    elif tab == 'hydropower-flow':
        attr = 'flow'
        for res in sorted(df_hydropower.columns):
            component = timeseries_component(attr, res, df_hydropower[res], df_obs)
            children.append(component)

    elif tab == 'ifr-flow':
        attr = 'flow'
        for res in sorted(df_ifr.columns):
            component = timeseries_component(
                attr, res, df_ifr[res], df_obs,
                min_reqt=df_ifr_reqt,
                # transform='log'
            )
            children.append(component)

    elif tab == 'ifr-range-flow':
        attr = 'flow'
        for res in sorted(df_pw_ifr.columns):
            component = timeseries_component(
                attr, res, df_pw_ifr[res], df_obs,
                min_reqt=df_pw_min_ifr_reqt,
                max_reqt=df_pw_max_ifr_reqt
            )
            children.append(component)

    elif tab == 'system':
        res = 'System'
        gauged_hp = [c for c in df_hydropower.columns if gauge_lookup.get(c) in df_obs]
        hp_gauges = [gauge_lookup[c] for c in gauged_hp]
        gauge_lookup[res] = res
        df_sim_system = df_hydropower[gauged_hp].sum(axis=1)  # should be series?
        df_obs_system = df_obs[hp_gauges].sum(axis=1).to_frame(res)
        hp_component = timeseries_component('flow', res, df_sim_system, df_obs_system)
        children.append(hp_component)

    return html.Div(
        children=children,
        className="timeseries-collection"
    )


if __name__ == '__main__':
    app.run_server(debug=False)
