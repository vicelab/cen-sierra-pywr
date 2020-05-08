BASINS = {
    'stn': 'Stanislaus',
    'tuo': 'Tuolumne',
    'mer': 'Merced',
    'usj': 'Upper San Joaquin'
}

ENSEMBLE_NAMES = {
    'mer': {
        'SWRCB 40': ['Baseline', '10%', '20%', '30%', '40%'],
        'District Reductions': ['Baseline', 'Reductions']
    },
    'stn': {
        'Price Year': ['PY2009', 'PY2060'],
        'SWRCB 40': ['Baseline', '40%'],
    }
}

PATH_TEMPLATES = {
    'mcm': '{run}/{basin}/{scenario}/{res_type}_{res_attr}_mcm.csv',
}

# PROD_RESULTS_PATH = r'C:\Users\david\Box\CERC-WET\Task7_San_Joaquin_Model\Pywr models\results'
PROD_RESULTS_PATH = r'C:\data'
# PROD_RESULTS_PATH = '../results'
DEV_RESULTS_PATH = '../results'

PCT_DIFF = 'PERCENT_DIFFERENCE'
ABS_DIFF = 'ABSOLUTE_DIFFERENCE'

PLOTLY_CONFIG = {
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['toggleSpikelines', 'sendDataToCloud', 'autoScale2d', 'zoomOut2d', 'zoomIn2d',
                               'editInChartStudio', 'boxSelect',
                               'lassoSelect'],
    'showLink': False,
}

MCM_TO_CFS = 1e6 / 24 / 3600 * 35.31
MCM_TO_TAF = 1 / 1.2335
