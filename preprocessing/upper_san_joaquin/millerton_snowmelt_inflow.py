import os
import pandas as pd


def calculate_millerton_snowmelt_inflow(scenario_path):

    # Read in the data
    inpath = os.path.join(scenario_path, 'preprocessed', 'full_natural_flow_daily_mcm.csv')
    df = pd.read_csv(inpath, index_col=0, header=0, parse_dates=True) / 1.2335 * 1000  # mcm to acre-feet

    # Filter by month (Apr-Jul) and resample by year
    df2 = df[df.index.map(lambda x: x.month in [4, 5, 6, 7])].resample('Y').sum()
    df2.index = df2.index.map(lambda x: x.year)
    df2.index.name = 'year'

    outpath = os.path.join(scenario_path, 'preprocessed', 'inflow_MillertonLake_AprToJul_af.csv')
    df2.to_csv(outpath)

    return
