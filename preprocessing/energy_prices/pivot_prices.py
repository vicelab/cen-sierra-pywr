import os
import pandas as pd
from calendar import isleap


def pivot_historical_prices():
    df = pd.read_csv('prices_historical.csv', names=['hour', 'price'], header=0)
    df.index = pd.date_range(start='2009-01-01', periods=len(df), freq='H')
    df['Hour'] = df.index.hour + 1
    df.index = [pd.Timestamp(r.strftime('%Y-%m-%d')) for r in df.index]
    df = df.pivot(columns='Hour', values='price')
    df.index.name = 'Date'

    sorted_reversed = [sorted(s, reverse=True) for s in df.values]
    df = pd.DataFrame(data=sorted_reversed, index=df.index, columns=df.columns)
    df.to_csv('./output/prices_pivoted_PY2009.csv')

    # Use this to extend years
    df2 = pd.DataFrame(index=pd.date_range(start='1980-01-01', end='2029-12-31', freq='D'), columns=df.columns)
    df2.index.name = 'Date'
    for date in df2.index:
        for col in df2.columns:
            if date.month == 2 and date.day == 29:
                lookup_date = pd.Timestamp(date.strftime('2009-02-28'))
            else:
                lookup_date = pd.Timestamp(date.strftime('2009-%m-%d'))
            df2.at[date, col] = df.at[lookup_date, col]
    df2.to_csv('./output/prices_pivoted_1980-2029.csv')

    return


def pivot_prices(dst):

    # First pivot historical prices
    pivot_historical_prices()

    # future data
    data = pd.read_csv('Price - After ES.csv', header=0, skiprows=[1], index_col=0)

    dfs = []
    for year in data:
        #     if int(year) not in [2030, 2045, 2060]:
        #         continue
        df = data[[year]].copy()
        df.index = pd.date_range(start=year + '-01-01', periods=len(df), freq='H')
        df['Hour'] = df.index.hour + 1
        df.index = [pd.Timestamp(r.strftime('%Y-%m-%d')) for r in df.index]
        df = df.pivot(columns='Hour', values=year)
        if isleap(int(year)):
            last_day = pd.Timestamp(int(year), 12, 31)
            last_row = df.iloc[-1]
            last_row.name = last_day
            df = df.append(last_row)
        df.columns = [str(c) for c in df.columns]
        df.index.name = 'Date'
        df.to_csv('./output/prices_pivoted_PY{}.csv'.format(int(year)))
        dfs.append(df)

    df = pd.concat(dfs, axis=0)

    df2 = pd.read_csv('pivot_energy_prices/output/prices_pivoted_PY2009.csv', parse_dates=True, index_col=0, header=0)
    df2.columns.name = 'Hour'

    df3 = pd.concat([df2, df])

    outpath = os.path.join(dst, 'prices_pivoted_select_years.csv')
    df3.to_csv(outpath)


if __name__ == '__main__':
    dst = 'pivot_energy_prices/output'
    pivot_prices(dst)
