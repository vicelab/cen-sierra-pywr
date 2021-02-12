from os import path, makedirs
import datetime as dt
from calendar import isleap
import pandas as pd


def pivot_prices(input_dir=None, output_dir=None):

    if not input_dir:
        input_dir = path.split(path.realpath(__file__))[0]

    if not output_dir:
        output_dir = path.join(path.split(path.realpath(__file__))[0], 'output')
        if not path.exists(output_dir):
            makedirs(output_dir)

    historical_path = path.join(input_dir, 'Historical Net Load and Electricity Price.csv')
    future_path = path.join(input_dir, 'NetLoad_for_UCM_2030_2060.csv')
    df_2009 = pd.read_csv(historical_path, index_col=0, header=0, skiprows=[0],
                          usecols=[0, 2], names=['Date', '2009'])
    df_future = pd.read_csv(future_path, index_col=0, header=0, skiprows=[1])
    df = pd.concat([df_2009, df_future], axis=1)

    pivoted = pd.DataFrame()

    for year in df.columns:
        _df = df[[year]].copy()
        # unstacked = _df.unstack().to_frame()
        starttime = dt.datetime(int(year), 1, 1)
        datetimes = [starttime + dt.timedelta(hours=h - 1) for h in _df.index]
        _df.index = pd.DatetimeIndex(datetimes)
        _df.reset_index(inplace=True)
        _df['Date'] = [dt.date(d.year, d.month, d.day) for d in datetimes]
        _df['hour'] = [d.hour + 1 for d in datetimes]

        _pivoted = _df.pivot(index='Date', columns='hour', values=year)

        if isleap(int(year)):
            last_day = pd.Timestamp(int(year), 12, 31)
            last_row = _pivoted.iloc[-1]
            last_row.name = last_day
            _pivoted = _pivoted.append(last_row)

        pivoted = pivoted.append(_pivoted)

    pivoted_path = path.join(output_dir, 'prices_pivoted_select_years.csv')
    pivoted.to_csv(pivoted_path)

    return


if __name__ == '__main__':
    pivot_prices()
