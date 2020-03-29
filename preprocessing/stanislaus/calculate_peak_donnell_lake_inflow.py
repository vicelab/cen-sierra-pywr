import os
import pandas as pd


def calculate_peak_donnell_lake_inflow(scenario_path):
    dfs = []
    for subwat in [18, 19, 20, 21]:
        path = os.path.join(scenario_path, 'runoff', 'tot_runoff_sb{}_mcm.csv'.format(subwat))
        df = pd.read_csv(path, header=0, index_col=0, parse_dates=True, names=['date', 'flow'])
        dfs.append(df)
    df = pd.concat(dfs)
    df['year'] = df.index.year
    grouped_df = df[df.index.map(lambda x: x.month in [3, 4, 5])].groupby('year')
    peak_flow_df = grouped_df.idxmax()
    peak_flow_df.columns = ['date']
    # peak_flow_df['flow'] = grouped_df.max()

    outpath = os.path.join(scenario_path, 'preprocessed', 'Donnells_Reservoir_Peak_MAM_Runoff_date.csv')
    peak_flow_df.to_csv(outpath)

    return
