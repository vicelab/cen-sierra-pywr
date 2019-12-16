import pandas as pd
import os

root_dir = '../data'
basins = ['merced', 'stanislaus']

for basin in os.listdir(root_dir):
    if 'River' not in basin:
        continue
    basin_dir = os.path.join(root_dir, basin)
    basin_runoff_dir = os.path.join(basin_dir, 'Scenarios', 'runoff')
    if not os.path.exists(basin_runoff_dir):
        continue
    print(basin)
    for scenario in os.listdir(basin_runoff_dir):
        scenario_dir = os.path.join(basin_runoff_dir, scenario)
        subwats = []
        if not os.path.exists(scenario_dir):
            continue
        print(scenario)
        for subwat in os.listdir(scenario_dir):
            path = os.path.join(scenario_dir, subwat)
            df = pd.read_csv(path, parse_dates=True, index_col=0, header=0)
            df.columns = [subwat.split('_')[2]]
            subwats.append(df)
        all_subwats_df = pd.concat(subwats, axis=1)

        # save to file
        outdir = os.path.join(basin_dir, 'Scenarios', 'postprocessed', scenario)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        all_subwats_df.to_csv(os.path.join(outdir, 'runoff_mcm.csv'))