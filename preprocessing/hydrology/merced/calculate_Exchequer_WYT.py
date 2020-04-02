import os
import pandas as pd


def calc_WY(flow):
    if flow >= 450:
        return 1
    else:
        return 2


def calculate_Exchequer_WYT(scenario_path):
    fnf_path = os.path.join(scenario_path, 'preprocessed', 'full_natural_flow_daily_mcm.csv')
    db = pd.read_csv(fnf_path, header=0, index_col=False, parse_dates=[0])
    db.columns = ['Date', 'Flow']
    db['Year'] = db["Date"].apply(lambda x: x.year)
    db['Month'] = db["Date"].apply(lambda x: x.month)
    db = db[(db['Month'] >= 4) & (db['Month'] <= 7)]
    db_agg = db.groupby(['Year']).agg({'Flow': 'sum'})
    db_agg = db_agg.reset_index()
    db_agg['Flow'] = db_agg[['Flow']] * 0.810713  # mcm to TAF
    db_agg['WYT'] = db_agg.apply(lambda x: pd.Series([calc_WY(x['Flow'])]), axis=1)
    db_agg.drop(columns=['Flow'], inplace=True)
    outpath = os.path.join(scenario_path, 'preprocessed', 'Exchequer_WYT.csv')
    db_agg.to_csv(outpath, index=False)
