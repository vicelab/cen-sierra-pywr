import os
from itertools import product
from datetime import datetime, timedelta
from preprocessing.scripts import create_forecasted_hydrology, create_full_natural_flow
from preprocessing.scripts import upper_san_joaquin as usj
# from preprocessing.scripts import stanislaus as stn

import pandas as pd

# basins = ['upper san joaquin']
basins = ['stanislaus']

root_dir = os.environ.get('SIERRA_DATA_PATH', '../data')

scenarios = ['Livneh']
gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
# scenarios += gcm_rcps

tasks = ["post"]

basin_scenarios = list(product(basins, scenarios))

for basin, scenario in basin_scenarios:

    basin_path = os.path.join(root_dir, '{} River'.format(basin.title()))
    scenarios_path = os.path.join(basin_path, 'Scenarios')
    basin_preprocessed_path = os.path.join(scenarios_path, 'preprocessed')

    # before processing hydrology
    if "pre" in tasks:
        if basin == 'upper san joaquin':
            usj.disaggregate_SJN_09_subwatershed(scenarios_path, scenario)

    # preprocess hydrology
    if "main" in tasks:
        create_forecasted_hydrology(root_dir, basin=basin, scenario=scenario)
        create_full_natural_flow(root_dir, basin=basin, scenario=scenario)

    if "post" in tasks:
        # Approximate DWR's 50% exceedance flows for the basin.
        fnf_path = os.path.join(basin_preprocessed_path, scenario, 'full_natural_flow_daily_mcm.csv')
        fnf_df = pd.read_csv(fnf_path, index_col=0, header=0, parse_dates=True)

        months = list(range(2, 9 + 1))
        years = sorted(list(set([dt.year for dt in fnf_df.index])))[1:]
        exceedances = [50]
        months_exceedances = list(product(months, exceedances))
        years_months = list(product(years, months))
        columns = pd.MultiIndex.from_tuples(months_exceedances)
        index = pd.MultiIndex.from_tuples(years_months)
        fnf_all = pd.DataFrame(index=index, columns=columns)

        for exceedance in exceedances:
            for year, month in years_months:

                ytg_monthly = []
                ytd_monthly = []

                # forecast year-to-go
                ytg_start = '{:04}-{:02}-01'.format(year, month)
                ytg_end = '{:04}-09-30'.format(year)

                if month <= 6:
                    # insert forecast routine here
                    ytg_monthly = fnf_df[ytg_start:ytg_end].resample('MS').sum()['flow'].values

                else:
                    # assume perfect year-to-go forecast after June
                    ytg_monthly = fnf_df[ytg_start:ytg_end].resample('MS').sum()['flow'].values


                # actual to-date
                if month > 2:
                    ytd_start = '{:04}-02-01'.format(year)
                    ytd_end = (datetime(year, month, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
                    ytd_monthly = fnf_df[ytd_start:ytd_end].resample('MS').sum()['flow'].values

                # aggregated
                ytd_ytg = list(ytd_monthly) + list(ytg_monthly)
                fnf_all.at[(year, month), ()] = ytd_ytg

            # sum across exceedance


        outpath = os.path.join(basin_preprocessed_path, scenario, 'fnf_forecast_mcm.csv')
        fnf_all.to_csv(outpath)

        # after processing hydrology
        if basin == 'upper san joaquin':
            usj.sjrrp_below_friant(basin_preprocessed_path, scenarios, 'full_natural_flow_annual_mcm.csv')
