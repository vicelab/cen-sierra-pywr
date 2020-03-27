import pandas as pd
import os


def create_full_natural_flow(root_dir, basin, scenario):
    basin_full = basin.title() + " River"
    basin_dir = os.path.join(root_dir, basin_full)
    scenario_dir = os.path.join(basin_dir, 'scenarios', scenario)
    basin_runoff_dir = os.path.join(scenario_dir, 'runoff_aggregated')
    if not os.path.exists(basin_runoff_dir):
        raise Exception('Basin path "{}" does not exist'.format(basin_runoff_dir))
    print(basin)

    subwats = []
    if not os.path.exists(scenario_dir):
        raise Exception('Scenario path "{}" does not exist'.format(scenario_dir))
    print(scenario)
    for filename in os.listdir(basin_runoff_dir):
        if '.csv' not in filename:
            continue
        path = os.path.join(basin_runoff_dir, filename)
        df = pd.read_csv(path, parse_dates=True, index_col=0, header=0)
        subwats.append(df)
    df = pd.concat(subwats, axis=1).sum(axis=1).to_frame()
    df.index.name = 'date'
    df.columns = ['flow']
    outdir = os.path.join(basin_dir, 'scenarios', scenario, 'preprocessed')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # daily
    df.to_csv(os.path.join(outdir, 'full_natural_flow_daily_mcm.csv'))

    # monthly
    df2 = df.resample('MS').sum()
    df2.to_csv(os.path.join(outdir, 'full_natural_flow_monthly_mcm.csv'))

    # annual
    df3 = df2.copy()
    df3['WY'] = [d.year if d.month <= 9 else d.year + 1 for d in df2.index]
    df3 = df3.reset_index().set_index('WY').drop('date', axis=1).groupby('WY').sum()
    df3.to_csv(os.path.join(outdir, 'full_natural_flow_annual_mcm.csv'))