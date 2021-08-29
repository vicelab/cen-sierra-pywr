import os
from itertools import product

import pandas as pd


def save_model_results(model, results_path, file_suffix, disaggregate=False, debug=False):
    results_df = model.to_dataframe()
    results_df.index.name = 'Date'
    scenario_names = [s.name for s in model.scenarios.scenarios]
    if not scenario_names:
        scenario_names = [0]
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    # if df_planning is not None:
    #     df_planning.to_csv(os.path.join(results_path, 'planning_debug.csv'))

    # Drop extraneous row
    has_scenarios = True
    recorder_items = set(results_df.columns.get_level_values(0))
    if len(results_df.columns) == len(recorder_items):
        has_scenarios = False
        results_df.columns = results_df.columns.droplevel(1)

    columns = {}
    # nodes_of_type = {}
    for c in results_df.columns:
        res_name, attr = (c[0] if has_scenarios else c).split('/')
        if res_name in model.nodes:
            node = model.nodes[res_name]
            _type = type(node).__name__
        else:
            _type = 'Other'
        key = (_type, attr)
        if key in columns:
            columns[key].append(c)
        else:
            columns[key] = [c]
        # nodes_of_type[_type] = nodes_of_type.get(_type, []) + [node]

    for (_type, attr), cols in columns.items():
        if attr == 'elevation':
            unit = 'm'
        elif attr == 'energy':
            unit = 'MWh'
        else:
            unit = 'mcm'
        # file_path = os.path.join(results_path, '{}_{}_{}_{}'.format(_type, attr.title(), unit, file_suffix))
        file_name = '{}_{}_{}.csv'.format(_type, attr.title(), unit)
        file_path = os.path.join(results_path, file_name)
        df = results_df[cols]
        if has_scenarios:
            if disaggregate:
                scenario_set_names = []
                for scenario_idx, scenario_set in enumerate(scenario_names):
                    scenario_set_names.append(list(set(df.columns.get_level_values(scenario_idx + 1))))
                scenario_combos = list(product(*scenario_set_names))
                for scenario_combo in scenario_combos:
                    scenario_name = '__'.join(scenario_combo)
                    scenario_path = os.path.join(results_path, scenario_name)
                    if not os.path.exists(scenario_path):
                        os.makedirs(scenario_path)

                    _df = df.copy()
                    for idx, scenario_set in enumerate(scenario_names):
                        _df = _df.xs(scenario_combo[idx], axis=1, level=scenario_set, drop_level=True)
                    file_path = os.path.join(scenario_path, file_name)
                    _df.columns = [c.split('/')[0] for c in _df.columns]
                    _df.to_csv(file_path)

            else:
                new_cols = [tuple([col[0].split('/')[0]] + list(col[1:])) for col in cols]
                df.columns = pd.MultiIndex.from_tuples(new_cols)
                df.columns.names = ["node"] + scenario_names
                df.to_csv(file_path)

        else:
            df.columns = [c.split('/')[0] for c in df.columns]
            df.to_csv(file_path)
