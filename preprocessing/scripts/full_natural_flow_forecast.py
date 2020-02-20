import os
from datetime import datetime
from itertools import product
import pandas as pd


def full_natural_flow_exceedance_forecast(basin_preprocessed_path, scenario):
    """
    This function calculates the full natural flow exceedance forecasts each month.
    Actually, for now it really does no such thing, and simply assumes perfect forecast. However, it can be updated
    with a real forecasting routine as needed. For now, the focus is on the Stanislaus River, Feb-Sep runoff.

    :param basin_preprocessed_path:
    :param scenario:
    :return:
    """


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
    fnf_all.index.names = ['year', 'month']
    fnf_all.columns.names = ['month', 'exceedance']
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
            fnf_all.loc[(year, month), (months, exceedance)] = ytd_ytg

        # sum across exceedance
        fnf_all[('sum', exceedance)] = fnf_all.loc[(years, months), (months, exceedance)].sum(axis=1)

    outpath = os.path.join(basin_preprocessed_path, scenario, 'fnf_forecast_mcm.csv')
    fnf_all.to_csv(outpath)
