import json
import pandas as pd
import os


def aggregate_subwatersheds(root_dir, basin, scenario):
    basin_full = basin.title() + " River"
    basin_dir = os.path.join(root_dir, basin_full)
    basin_runoff_dir = os.path.join(basin_dir, 'Scenarios', 'runoff')
    if not os.path.exists(basin_runoff_dir):
        raise Exception('Basin path "{}" does not exist'.format(basin_runoff_dir))

    scenario_dir = os.path.join(basin_runoff_dir, scenario)
    if not os.path.exists(scenario_dir):
        raise Exception('Scenario path "{}" does not exist'.format(scenario_dir))

    subwat_groups = {}

    # collect subwatersheds
    model_path = '../{}/temp/pywr_model_Livneh_simplified.json'.format(basin.replace(' ', '_'))
    with open(model_path) as f:
        model = json.load(f)

    for n1, n2 in model['edges']:
        if ' Headflow' in n1:
            subwat_groups[n2] = subwat_groups.get(n2, []) + [n1]

    runoff_data = []
    for subwat_group, subwats in subwat_groups.items():
        subwat_group_name = '{} Inflow'.format(subwat_group)
        subwat_group_runoff = []
        for subwat in subwats:
            filename = 'tot_runoff_sb{}_mcm.csv'.format(subwat.split(' ')[0].split('_')[1])
            path = os.path.join(scenario_dir, filename)
            df = pd.read_csv(path, parse_dates=True, index_col=0, header=0)
            subwat_group_runoff.append(df)
        df = pd.concat(subwat_group_runoff, axis=1).sum(axis=1).to_frame()
        df.index.name = 'date'
        df.columns = [subwat_group_name]

        outdir = os.path.join(basin_dir, 'Scenarios', 'runoff_aggregated', scenario)
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        df.to_csv(os.path.join(outdir, '{} mcm.csv'.format(subwat_group_name)))

    return