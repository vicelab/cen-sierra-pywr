import pandas as pd

dir = r"C:\Users\Aditya\Box Sync\VICE Lab\RESEARCH\PROJECTS\CERC-WET\Task7_San_Joaquin_Model\Pywr models\data\Stanislaus River"
scenarios = ['Livneh','CanESM2_rcp45','CanESM2_rcp85','CNRM-CM5_rcp45','CNRM-CM5_rcp85','HadGEM2-ES_rcp45','HadGEM2-ES_rcp85','MIROC5_rcp45','MIROC5_rcp85']

def assign_WYT(row):
    if row['Flow'] <= 140000:
        x = 1
    elif row['Flow'] <= 320000:
        x = 2
    elif row['Flow'] <= 400000:
        x = 3
    elif row['Flow'] <= 500000:
        x = 4
    else:
        x = 5
    return x

for scn in scenarios:
    # TODO: update to read in fnf file
    apr_jul_inflow_df = pd.read_csv(dir+ "\scenarios\preprocessed\{}\inflow_NewMelones_AprToJul_AF.csv".format(scn),names=['WY','Flow'], header=0,index_col=False)
    apr_jul_inflow_df['WYT'] = apr_jul_inflow_df.apply(lambda row: assign_WYT(row), axis=1)
    print(apr_jul_inflow_df.head())
    new_db = apr_jul_inflow_df[['WY','WYT']]
    print(new_db.head())
    new_db.to_csv(dir+ "\scenarios\preprocessed\{}\WYT_P2019.csv".format(scn),index=False)