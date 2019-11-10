# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import plotly.graph_objs as go

import dash_daq as daq

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

obs_stor_file = '../data/{basin}/gauges/storage_cleaned.csv'
results_file = '../{basin}/results/with optimization/tables/{res_type}_{res_attr}.csv'
basin = 'stanislaus'

df_storage = pd.read_csv(
    results_file.format(basin=basin, res_type='Storage', res_attr='Storage'),
    index_col=[0],
    parse_dates=True
)
df_obs = pd.read_csv(
    obs_stor_file.format(basin=basin.replace('_', ' ').title() + ' River'),
    index_col=[0],
    parse_dates=True
).loc[df_storage.index]


def performance_metric_gauge(id, value, min=0.0, max=1.0):
    return daq.Gauge(
        id=id,
        size=120,
        min=min,
        value=value,
        max=max,
        color={
            "gradient": True,
            "ranges": {
                "red": [0, 6],
                "yellow": [6, 8],
                "green": [8, 10]
            }
        },
    )


def make_timeseries_component(attr, res_name):
    res_name_id = res_name.lower().replace(' ', '_')
    sim_vals = df_storage[res_name]
    data = [
        go.Scatter(
            x=df_storage.index,
            y=sim_vals,
            text='Simulated',
            mode='lines',
            opacity=0.7,
            name='Simulated'
        )
    ]

    gauges = []
    if res_name in df_obs:
        obs_vals = df_obs[res_name]
        data.append(
            go.Scatter(
                x=df_obs.index,
                y=obs_vals,
                text='Observed',
                mode='lines',
                opacity=0.7,
                name='Observed'
            )
        )

        pbias = sim_vals.mean() / obs_vals.mean() - 1
        _max = max(1.0, pbias)
        gauge1 = performance_metric_gauge('gauge1-' + res_name_id, pbias, min=-1.0, max=_max)

        gauges = [gauge1]

    graph = dcc.Graph(
        id='storage-' + res_name.replace(' ', '-'),
        className='timeseries-chart',
        config={
            'displayModeBar': False
        },
        figure={
            'data': data,
            'layout': go.Layout(
                title=res_name,
                xaxis={'title': 'Date'},
                yaxis={'title': 'Storage (mcm)'},
                margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
            )
        }
    )

    children = [graph] + gauges

    div = html.Div(
        children=children,
        className="timeseries-collection"
    )

    return div


app.layout = html.Div(children=[
    html.H1(children='Hello California!'),

    html.Div(children='''
        A visualization tool for debugging SIERRA2.
    '''),

    html.Div(
        [make_timeseries_component('storage', res) for res in df_storage.columns],
        className="timeseries-collection"
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
