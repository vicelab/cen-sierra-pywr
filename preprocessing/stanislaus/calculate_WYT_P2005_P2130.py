import os
import pandas as pd
import datetime

dir = r"C:\Users\Aditya\Box Sync\VICE Lab\RESEARCH\PROJECTS\CERC-WET\Task7_San_Joaquin_Model\Pywr models\data\Stanislaus River"
scenarios = ['Livneh','CanESM2_rcp45','CanESM2_rcp85','CNRM-CM5_rcp45','CNRM-CM5_rcp85','HadGEM2-ES_rcp45','HadGEM2-ES_rcp85','MIROC5_rcp45','MIROC5_rcp85']

def assign_WYT(row):
    if row['Inflow_AF'] <= 350000:
        x = 1
    elif row['Inflow_AF'] <= 676000:
        x = 2
    elif row['Inflow_AF'] <= 1050000:
        x = 3
    elif row['Inflow_AF'] <= 1585000:
        x = 4
    else:
        x = 5
    return x


def assign_WY(row):
    if row['Date'].month in [10,11,12]:
        x = row['Date'].year+1
    else:
        x = row['Date'].year
    return x

for scn in scenarios:
    inflow_melones = pd.read_csv(dir + "/Scenarios/preprocessed/{}/full_natural_flow_daily_mcm.csv".format(scn), names=['Date', 'T_flw'], header=0, parse_dates=[0])  # mcm
    inflow_melones['WY'] = inflow_melones.apply (lambda row: assign_WY(row), axis=1)
    df = inflow_melones.groupby('WY')['T_flw'].sum()*810.71318 #mcm to AF
    df1 = df.to_frame()
    df1.columns = ['Inflow_AF']
    #df1 = df1.unstack()
    # df1.to_csv(dir+ "\Scenarios\preprocessed\{}\inflow_annual_LakeMelones_AF.csv".format(scn))
    # annual_inflow_df = pd.read_csv(dir + "\Scenarios\preprocessed\{}\inflow_annual_LakeMelones_AF.csv".format(scn),names=['WY','Inflow_AF'], header=0,index_col=False)
    annual_inflow_df = df1
    print(annual_inflow_df.head())

    annual_inflow_df['WYT'] = annual_inflow_df.apply(lambda row: assign_WYT(row), axis=1)
    print(annual_inflow_df.head())
    new_db = annual_inflow_df[['WY','WYT']]
    print(new_db.head())
    new_db.to_csv(dir + "\Scenarios\preprocessed\{}\WYT_P2005_P2130.csv".format(scn),index=False)