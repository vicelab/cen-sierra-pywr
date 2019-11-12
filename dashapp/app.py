# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objs as go

import dash_daq as daq

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

opath = '../data/{basin}/gauges/{attr}.csv'
rpath = '../{basin}/results/with optimization/tables/{res_type}_{res_attr}.csv'
basin = 'stanislaus'

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

df_hydropower = pd.concat([df_hp1, df_hp2], axis=1)

df_ifr = pd.read_csv(
    rpath.format(basin=basin, res_type='InstreamFlowRequirement', res_attr='Flow'),
    index_col=[0],
    parse_dates=True,
)

df_ifr_reqt = pd.read_csv(
    rpath.format(basin=basin, res_type='InstreamFlowRequirement', res_attr='Requirement'),
    index_col=[0],
    parse_dates=True,
)

df_obs_storage = pd.read_csv(
    opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='storage'),
    index_col=[0],
    parse_dates=True
).loc[df_storage.index]

df_obs_streamflow = pd.read_csv(
    opath.format(basin=basin.replace('_', ' ').title() + ' River', attr='streamflow'),
    index_col=[0],
    parse_dates=True
).loc[df_hydropower.index].ffill()

gauge_lookup = pd.read_csv('gauges.csv', index_col=[0], squeeze=True, dtype=(str)).to_dict()


def root_mean_square_error(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def nash_sutcliffe_efficiency(predictions, targets):
    slope, intercept, r_value, p_value, std_err = stats.linregress(predictions, targets)
    return r_value ** 2


def percent_bias(predictions, targets):
    return predictions.mean() / targets.mean() - 1


def timeseries_component(attr, res_name, sim_vals, df_obs, req_vals=None):
    res_name_id = res_name.lower().replace(' ', '_')
    data = []

    if req_vals is not None:
        data.append(
            go.Scatter(
                x=req_vals.index,
                y=req_vals,
                text='Requirement',
                mode='lines',
                opacity=0.7,
                name='Requirement',
                line=go.scatter.Line(color='red')
            )
        )

    data.append(
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

    gauges = []
    gauge_name = gauge_lookup.get(res_name, res_name)

    if gauge_name not in df_obs:
        obs_vals = np.zeros(len(df_obs))
        pbias = 100
        nse = -1

    else:
        obs_vals = df_obs[gauge_name]

        predictions = sim_vals.values
        targets = obs_vals.loc[sim_vals.index].values

        pbias = percent_bias(predictions, targets) * 100
        rmse = root_mean_square_error(predictions, targets)
        nse = nash_sutcliffe_efficiency(predictions, targets)

    obs_graph = go.Scatter(
        x=df_obs.index,
        y=obs_vals,
        text='Observed',
        mode='lines',
        opacity=0.7,
        name='Observed',
        line=go.scatter.Line(color='darkgrey')
    )
    data.insert(0, obs_graph)

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
        ylabel = 'Storage (mcm)'
    else:
        ylabel = 'Flow (mcm/day)'
    graph = dcc.Graph(
        id='storage-' + res_name_id,
        className='timeseries-chart',
        config={
            'displayModeBar': False
        },
        figure={
            'data': data,
            'layout': go.Layout(
                # title=res_name,
                xaxis={'title': 'Date'},
                yaxis={'title': ylabel},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
            )
        }
    )

    children = [graph] + gauges

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


app.title = 'SJMS'
app.layout = html.Div(children=[
    html.H1(children='San Joaquin Modeling System'),

    dcc.Tabs(id="timeseries-tabs", value='reservoir-storage', children=[
        dcc.Tab(label='Reservoir storage', value='reservoir-storage'),
        dcc.Tab(label='PH flow', value='hydropower-flow'),
        dcc.Tab(label='IFR flow', value='ifr-flow'),
    ]),
    html.Div(id='timeseries-tabs-content')
])


@app.callback(Output('timeseries-tabs-content', 'children'),
              [Input('timeseries-tabs', 'value')])
def render_content(tab):
    df_reqt = None

    if tab == 'reservoir-storage':
        attr = 'storage'
        df = df_storage
        df_obs = df_obs_storage

    elif tab == 'hydropower-flow':
        attr = 'flow'
        df = df_hydropower
        df_obs = df_obs_streamflow

    elif tab == 'ifr-flow':
        attr = 'flow'
        df = df_ifr
        df_obs = df_obs_streamflow
        df_reqt = df_ifr_reqt

    children = []
    for res in sorted(df.columns):
        req_vals = None
        if df_reqt is not None:
            req_vals = df_ifr_reqt[res]
        component = timeseries_component(attr, res, df[res], df_obs, req_vals=req_vals)
        children.append(component)

    return html.Div(
        children=children,
        className="timeseries-collection"
    )


if __name__ == '__main__':
    app.run_server(debug=False)
