import pandas as pd
import os


def create_full_natural_flow(root_dir, basins=None):
    basins = basins or ['merced', 'stanislaus', 'upper san joaquin', 'tuolumne']
    for basin in basins:
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
                subwats.append(df)
            df = pd.concat(subwats, axis=1).sum(axis=1).to_frame()
            df.index.name = 'date'
            df.columns = ['flow']
            outdir = os.path.join(basin_dir, 'Scenarios', 'preprocessed', scenario)
            df.to_csv(os.path.join(outdir, 'full_natural_flow_daily_mcm.csv'))
            df.resample('MS').sum().to_csv(os.path.join(outdir, 'full_natural_flow_monthly_mcm.csv'))
