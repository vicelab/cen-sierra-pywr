# -*- coding: utf-8 -*-
import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as leaflet
from dash.dependencies import Input, Output, State

import json
import pandas as pd
import plotly.graph_objs as go

import dash_daq as daq

import dashapp.constants as c
from dashapp.constants import BASINS, ENSEMBLE_NAMES, MCM_TO_TAF
from dashapp.components import timeseries_collection

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

opath = '../data/{basin}/gauges/{attr}.csv'

source_text = {'simulated': 'Simulated', 'observed': 'Observed'}
# source_name = {'simulated': 'Simulated'}
source_color = {'simulated': 'blue', 'observed': 'darkgrey'}

GCMS = ['Livneh', 'HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
RCPS = ['rcp45', 'rcp85']

RES_OPTIONS = {}
SCENARIOS = {}

# STYLES

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
    # "marginLeft": "5rem",
    # "margin-right": "2rem",
    "padding": "2rem 1rem",
}

SIDEBAR_TABS = [
    {
        'label': 'Map',
        'href': '/map',
        'id': 'map-tab'
    },
    {
        'label': 'Schematics',
        'href': '/schematics',
        'id': 'schematics-tab'
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


# =================

def register_basin_callbacks(basin, basin_scenarios):
    scenario_inputs = [Input(s['name'].replace(' ', '-'), 'value') for s in basin_scenarios]

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
            basin_scenarios=basin_scenarios,
            transform=transform,
            resample=resample,
            aggregate=aggregate,
            consolidate=consolidate,
            percentiles=percentiles,
            percentiles_type=percentiles_type,
            run_name='full run 2019-12-19',
            selected_scenarios=selected_scenarios,
            gauge_lookup=gauge_lookup,
            df_obs_streamflow=df_obs_streamflow,
            df_obs_storage=df_obs_storage
        )
        return timeseries_collection(tab, **kwargs)


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

gauge_lookup = pd.read_csv('gauges.csv', header=None, index_col=0, squeeze=True, dtype=(str)).to_dict()

percentile_colors = {
    'simulated': 'blue',
    'observed': 'grey'
}


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
        config=c.PLOTLY_CONFIG,
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
        # dcc.Dropdown(
        #     id='select-basins-global',
        #     options=[
        #         {'label': 'Stanislaus', 'value': 'stn'},
        #         {'label': 'Tuolumne', 'value': 'tuo'},
        #         {'label': 'Merced', 'value': 'mer'},
        #         {'label': 'Upper San Joaquin', 'value': 'usj'},
        #     ],
        #     value=['stn', 'tuo', 'mer', 'usj'],
        #     multi=True
        # )
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
    sticky="top",
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

select_metric = dbc.FormGroup(
    [
        dbc.Label("Metric", html_for="select-metric", width=2),
        # dbc.RadioItems(
        #     id="radio-metric",
        #     options=[
        #         {"label": "None", "value": None},
        #         {"label": "Percent difference", "value": c.PCT_DIFF},
        #         {"label": "Absolute difference", "value": c.ABS_DIFF},
        #     ],
        #     value=None,
        #     # inline=True
        # ),
        dcc.Dropdown(
            id="select-metric",
            options=[
                {"label": "None", "value": "default"},
                {"label": "Percent difference", "value": c.PCT_DIFF},
                {"label": "Absolute difference", "value": c.ABS_DIFF},
            ],
            value="default"
        )
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
    options=[{"label": BASINS[basin], "value": basin} for basin in BASINS],
    value=None,
    style={'minWidth': '200px'},
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
], inline=True, style={"marginBottom": "10px"})

development_selections = dbc.Form([
    dbc.FormGroup([
        select_development_basin
    ])
], inline=True, style={"marginBottom": "10px"})

layout_switches = dbc.FormGroup(
    [
        dbc.Label("Layout"),
        dbc.Checklist(
            id="layout-options",
            options=[
                {"label": "Compact", "value": "compact"},
                {"label": "FD curves", "value": "flow-duration"},
                # {"label": "Disabled Option", "value": 3, "disabled": True},
            ],
            value=["flow-duration"],
            switch=True,
        ),
    ]
)


def make_controls(mode='production'):
    controls = [layout_switches, transform_radio, resample_radio, aggregate_radio, consolidation_checklist]
    if mode == 'development':
        controls = [select_metric] + controls
    return dbc.Form(
        controls,
        id='sidebar-controls',
        className='sidebar-controls',
        inline=False
    )


top_bar = dbc.Form(
    [
        dbc.FormGroup([
            dcc.Dropdown(
                options=[],
                id='select-resources',
                className='select-resources',
                style={'minWidth': '300px'},
                multi=True,
                value=[],
                placeholder='Select a resource...'
            ),
            dbc.Button([
                'Reload'
            ], id='reload', style={'marginLeft': 'auto'})
        ], style={'display': 'inline-flex', 'marginTop': '5px', 'width': '100%'})
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
    return html.Div(
        [
            dbc.Row([
                dbc.Col([
                    html.Div(children=[
                        selections,
                        scenario_selections,
                        dbc.Tabs(id="development-tabs", active_tab='reservoir-storage', children=[
                            # dbc.Tab(label='System', tab_id='system'),
                            dbc.Tab(label='Reservoir storage', tab_id='reservoir-storage'),
                            dbc.Tab(label='HP flow', tab_id='hydropower-flow'),
                            # dbc.Tab(label='HP generation', tab_id='hydropower-generation'),
                            dbc.Tab(label='IFR flow', tab_id='ifr-flow'),
                            # dbc.Tab(label='IFR flow (range)', tab_id='ifr-range-flow'),
                            dbc.Tab(label='Outflow', tab_id='outflow'),
                            dbc.Tab(label='Mixed', tab_id='mixed')
                        ]),
                        top_bar,
                        main_content
                    ])],
                    width=12
                )
            ]),
            make_controls(mode=purpose)
        ],
        style={'width': '100%'}
    )


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
            children=[]),
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


@app.callback(Output('main-content', 'style'), [
    Input('url', 'pathname')
])
def update_css(pathname):
    style = dict(
        display='inline-flex',
        padding='15px',
        position='fixed',
        left='10rem',
        right='0',
        top=55,
        bottom=0
    )
    if '/development' in pathname or '/scenarios' in pathname:
        style.update(
            right='255px'
        )
    return style


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


# @app.callback(Output("select-basin", "options"), [
#     Input("select-basins-global", "value")
# ])
# def render_select_development_basin_options(basins):
#     return [{"label": BASINS[basin], "value": basin} for basin in basins]


# @app.callback(Output("select-basin", "value"), [
#     Input("select-basins-global", "value")
# ])
# def render_select_development_basin_value(basins):
#     return basins[0]


@app.callback(Output("sidebar-tabs", "children"), [Input("url", "pathname")])
def render_sidebar_tabs(pathname):
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
    elif pathname == '/schematics':
        return render_schematics_content()
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


def render_schematics_content():
    basin_schematic_tabs = []
    for code, name in BASINS.items():
        basin_schematic_tabs.append(
            dbc.Tab(label=name, tab_id=code)
        )

    return html.Div([
        dbc.Tabs(id="schematics-tabs", active_tab='stn', children=basin_schematic_tabs),
        html.Div(
            id='schematics-content',
            children=[html.Div('test')],
        )
    ], style={"width": "100%"})


@app.callback(Output('schematics-content', 'children'), [
    Input('schematics-tabs', 'active_tab')
])
def update_schematic(basin_code):
    basin_name = BASINS[basin_code].replace(' ', '_').lower()
    return [html.Embed(
        src=app.get_asset_url('schematics/{}_schematic_simplified.gv.pdf'.format(basin_name)),
        type='application/pdf',
        className='schematic-pdf',
        width="100%",
        height="100%"
    )]


@app.callback(Output('map-content', 'children'), [
    Input('show-map-labels', 'value')
])
def render_map(show_labels):
    show_labels = 'show-all-labels' in show_labels
    simplify = False
    nodes = []
    links = []
    lats = []
    lons = []
    tt_paths = {}
    for i, (abbr, full_name) in enumerate(BASINS.items()):
        oa_network_path = '../openagua_schematics/{} River.json'.format(full_name)
        if not os.path.exists(oa_network_path):
            continue
        with open(oa_network_path) as f:
            oa_network = json.load(f)
        pywr_model_path = '../{}/temp/pywr_model_Livneh_simplified.json'.format(full_name.replace(' ', '_').lower())
        if not os.path.exists(pywr_model_path):
            continue
        with open(pywr_model_path) as f:
            pywr_network = json.load(f)

        net = oa_network['network']
        tmpl = oa_network['template']
        node_lookup = {n['name']: n for n in net['nodes']}

        if i == 0:
            for tt in tmpl['templatetypes']:
                tt_name = tt['name']
                tt_svg = tt['layout'].get('svg')
                if not tt_svg:
                    continue
                tt_path = './icons/{}.svg'.format(tt_name.replace(' ', '_'))
                with open(os.path.join('./assets', tt_path), 'w') as f:
                    f.write(tt_svg)
                tt_paths[tt['name']] = tt_path

        if simplify:
            for n in pywr_network['nodes']:
                if n['name'] not in node_lookup:
                    continue
                node = node_lookup[n['name']]
                lat, lon = float(node['y']), float(node['x'])
                lats.append(lat)
                lons.append(lon)
                nodes.append(
                    leaflet.Marker(
                        position=[lat, lon]
                    )
                )

            for n1, n2 in pywr_network['edges']:
                if n1 not in node_lookup or n2 not in node_lookup:
                    continue
                node1 = node_lookup[n1]
                node2 = node_lookup[n2]
                lat1, lon1 = float(node1['y']), float(node1['x'])
                lat2, lon2 = float(node2['y']), float(node2['x'])
                positions = [[lat1, lon1], [lat2, lon2]]
                links.append(
                    leaflet.Polyline(
                        positions=positions
                    )
                )
        else:
            for node in net['nodes']:
                lat, lon = float(node['y']), float(node['x'])
                tt = [t for t in node['types'] if t['template_id'] == tmpl['id']][-1]

                tt_path = tt_paths.get(tt['name'])
                kwargs = {}
                if tt_path:
                    if tt['name'].lower() == 'junction' or 'gauge' in tt['name'].lower():
                        size = 12
                    else:
                        size = 24
                    kwargs.update(
                        icon=dict(
                            iconUrl=app.get_asset_url(tt_path),
                            iconSize=[size, size],
                            iconAnchor=[size/2, size/2]
                        )
                    )
                nodes.append(
                    leaflet.Marker(
                        position=[lat, lon],
                        **kwargs
                    )
                )
                lats.append(lat)
                lons.append(lon)
            for link in net['links']:
                coords = link['layout']['geojson']['geometry']['coordinates']
                lons_, lats_ = zip(*coords)
                positions = list(zip(*[lats_, lons_]))
                tt = [t for t in link['types'] if t['template_id'] == tmpl['id']][-1]
                linestyle = tt['layout'].get('linestyle')
                if type(linestyle) == str:
                    try:
                        linestyle = json.loads(linestyle)
                    except:
                        linestyle = {}
                links.append(
                    leaflet.Polyline(
                        positions=positions,
                        **linestyle
                    )
                )

    clat = (min(lats) + max(lats)) / 2
    clon = (min(lons) + max(lons)) / 2

    return [
        leaflet.Map(style={'width': '100%', 'height': '100%'}, center=[clat, clon], zoom=9, children=[
            leaflet.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            leaflet.LayerGroup(
                children=nodes + links
            )
        ])
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
                  Input('select-metric', 'value'),
                  Input('radio-transform', 'value'),
                  Input('radio-resample', 'value'),
                  Input('radio-aggregate', 'value'),
                  Input('percentiles-checklist', 'value'),
                  Input('percentiles-options', 'value'),
                  Input('percentiles-type', 'value'),
                  Input('layout-options', 'value'),
                  Input('select-resources', 'value'),
                  Input('reload', 'n_clicks'),
              ])
def render_development_content(tab, basin, metric, transform, resample, aggregate, consolidate, percentiles,
                               percentiles_type, layout_options, resources, n_clicks):
    kwargs = dict(
        basin=basin,
        resources=resources,
        basin_scenarios=basin_scenarios,
        metric=metric,
        transform=transform,
        resample=resample,
        aggregate=aggregate,
        consolidate=consolidate,
        percentiles=percentiles,
        percentiles_type=percentiles_type,
        layout_options=layout_options,
        run_name='development',
        gauge_lookup=gauge_lookup,
        df_obs_streamflow=df_obs_streamflow,
        df_obs_storage=df_obs_storage
    )
    return timeseries_collection(tab, **kwargs)


if __name__ == '__main__':
    app.run_server(debug=False)
