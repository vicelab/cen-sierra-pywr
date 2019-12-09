from itertools import product

from dash.dependencies import Input, Output, State
from dashapp import app


def register_basin_callbacks(basin, scenarios):
    scenario_inputs = [Input(s['name'].replace(' ', '-'), 'value') for s in scenarios]

    @app.callback(Output('analysis-tabs-content', 'children'),
                  [
                      Input('diagnostics-tabs', 'active_tab'),
                      Input('radio-transform', 'value'),
                      Input('radio-resample', 'value'),
                      Input('percentiles-checklist', 'value'),
                      Input('select-basin', 'value'),
                      Input('select-climate', 'value'),
                      Input('select-price-year', 'value'),
                      Input('select-resources', 'value'),
                      Input('reload', 'n_clicks')
                  ] + scenario_inputs)
    def render_analysis_content(tab, transform, resample, percentiles, basin, climates, priceyears, resources, n_clicks,
                                **scenario_kwargs):
        selected_scenarios = product(scenario_kwargs.values())
        kwargs = dict(
            basin=basin,
            climates=climates,
            priceyears=priceyears,
            resources=resources,
            transform=transform,
            resample=resample,
            percentiles=percentiles,
            run_name='full run',
            selected_scenarios=selected_scenarios
        )
        return render_timeseries_collection(tab, **kwargs)
