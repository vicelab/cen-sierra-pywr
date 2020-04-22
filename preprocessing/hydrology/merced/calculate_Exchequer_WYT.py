import os
import pandas as pd


def calc_WY(flow):
    if flow >= 450:
        return 1
    else:
        return 2


def calculate_Exchequer_WYT(scenario_path):
    fnf_path = os.path.join(scenario_path, 'preprocessed', 'full_natural_flow_daily_mcm.csv')
    df = pd.read_csv(fnf_path, header=0, index_col=0, parse_dates=True, names=['flow'])
    df2 = df[(df.index.month >= 4) & (df.index.month <= 7)]
    df3 = df2.resample('Y').sum()
    df3 /= 1.2335  # mcm to TAF

    # compute the water year type
    df3['WYT'] = df3['flow'].apply(lambda x: 1 if x >= 450 else 2)
    df3.index = df3.index.year
    df3.index.name = 'WY'

    # create the final WYT dataframe, adding an initial WYT to the beginning
    wyt_df = pd.Series(index=[df3.index[0] - 1] + list(df3.index))
    wyt_df[wyt_df.index[0]] = 3  # assume the previous water year's type is 3
    wyt_df.values[1:] = df3['WYT']
    wyt_df.index.name = 'WY'
    wyt_df.name = 'WYT'

    outpath = os.path.join(scenario_path, 'preprocessed', 'Exchequer_WYT.csv')
    wyt_df.to_csv(outpath)
