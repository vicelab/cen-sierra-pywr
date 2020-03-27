import pandas as pd

####################################
rcp = 85
scen = ['CanESM2_rcp{}'.format(rcp),'CNRM-CM5_rcp{}'.format(rcp),'HadGEM2-ES_rcp{}'.format(rcp),'MIROC5_rcp{}'.format(rcp)]
o_path = r"C:\Users\Aditya\Box Sync\VICE Lab\RESEARCH\PROJECTS\CERC-WET\Task7_San_Joaquin_Model\Pywr models\data\Merced River\Scenarios\preprocessed"

def calc_WY(flw):
    if flw >= 450:
        return 1
    else:
        return 2

for s in scen:
    db = pd.read_csv(o_path + '\{}'.format(s) + '\\full_natural_flow_daily_mcm.csv', header=0, index_col=False, parse_dates=[0])
    db.columns = ['Date', 'Flow']
    db['Year'] = db["Date"].apply(lambda x: x.year)
    db['Month'] = db["Date"].apply(lambda x: x.month)
    db = db[(db['Month'] >= 4) & (db['Month'] <= 7)]
    db_agg = db.groupby(['Year']).agg({'Flow': 'sum'})
    db_agg = db_agg.reset_index()
    db_agg['Flow'] = db_agg[['Flow']]*0.810713 #mcm to TAF
    db_agg['WYT'] = db_agg.apply(lambda x: pd.Series([calc_WY(x['Flow'])]), axis=1)
    db_agg.drop(columns=['Flow'], inplace=True)
    print(db_agg.head())
    db_agg.to_csv(o_path + '\{}\Exchequer_WYT.csv'.format(s), index=False)