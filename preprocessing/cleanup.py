obsolete_files = {
    'all': [
        'scenarios/preprocessed/{scenario}/runoff_mcm.csv',
        'scenarios/preprocessed/{scenario}/runoff_aggregated_mcm.csv'
    ],
    'merced': [
        'scenarios/preprocessed/{scenario}/WYT.csv'
    ],
    'stanislaus': [
        'scenarios/preprocessed/{scenario}/inflow_annual_LakeMelones_AF.csv',
        'scenarios/preprocessed/{scenario}/inflow_daily_LakeMelones_mcm.csv',
        'scenarios/preprocessed/{scenario}/inflow_NewMelones_AprToJul_AF.csv',
        'scenarios/preprocessed/{scenario}/stanislaus_WYT.csv',
        'scenarios/preprocessed/{scenario}/tot_runoff_DonnellsRes.csv',
        'scenarios/preprocessed/{scenario}/tot_runoff_sbAll.csv',
    ],
    'upper_san_joaquin': [
        'scenarios/preprocessed/{scenario}/Inflow_MillertonLake_daily_cms.csv',
        'scenarios/preprocessed/{scenario}/SJ restoration flows WYT.csv',
    ]
}
obsolete_folders = {
    'all': [
        'scenarios/runoff_monthly'
    ]
}


def cleanup_files():
    return


if __name__ == '__main__':
    cleanup_files()
