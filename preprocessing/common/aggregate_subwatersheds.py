import json
import pandas as pd
import os

from utilities import simplify_network


def aggregate_subwatersheds(scenario_path, basin):
    """
    Some description...
    :param scenario_path:
    :param basin:
    :return:
    """
    if not os.path.exists(scenario_path):
        raise Exception('Scenario path "{}" does not exist'.format(scenario_path))

    basin_runoff_dir = os.path.join(scenario_path, 'runoff')
    if not os.path.exists(basin_runoff_dir):
        raise Exception('Basin path "{}" does not exist'.format(basin_runoff_dir))

    subwat_groups = {}

    # collect subwatersheds
    model_path = '../{}/pywr_model.json'.format(basin.replace(' ', '_'))
    with open(model_path) as f:
        full_model = json.load(f)
    model = simplify_network(full_model, scenario_path=scenario_path, delete_gauges=True, delete_observed=True,
                             delete_scenarios=True,
                             aggregate_runoff=False)

    for n1, n2 in model['edges']:
        if ' Headflow' in n1:
            subwat_groups[n2] = subwat_groups.get(n2, []) + [n1]

    runoff_data = []
    for subwat_group, subwats in subwat_groups.items():
        subwat_group_name = '{} Inflow'.format(subwat_group)
        subwat_group_runoff = []
        for subwat in subwats:
            filename = 'tot_runoff_sb{}_mcm.csv'.format(subwat.split(' ')[0].split('_')[1])
            path = os.path.join(scenario_path, 'runoff', filename)
            df = pd.read_csv(path, parse_dates=True, index_col=0, header=0)
            subwat_group_runoff.append(df)
        df = pd.concat(subwat_group_runoff, axis=1).sum(axis=1).to_frame()
        df.index.name = 'date'
        df.columns = ["flow"]

        outdir = os.path.join(scenario_path, 'runoff_aggregated')
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        df.to_csv(os.path.join(outdir, '{} mcm.csv'.format(subwat_group_name)))

    return
