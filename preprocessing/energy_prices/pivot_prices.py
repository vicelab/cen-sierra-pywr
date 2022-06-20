import os
from pathlib import Path
import pandas as pd
from calendar import isleap


def pivot_historical_prices(src, tmp_dir):
    prices_path = Path(src, 'Historical Net Load and Electricity Price.csv')
    df = pd.read_csv(prices_path, names=['hour', 'price'], header=0)
    df.index = pd.date_range(start='2009-01-01', periods=len(df), freq='H')
    df['Hour'] = df.index.hour + 1
    df.index = [pd.Timestamp(r.strftime('%Y-%m-%d')) for r in df.index]
    df = df.pivot(columns='Hour', values='price')
    df.index.name = 'Date'

    sorted_reversed = [sorted(s, reverse=True) for s in df.values]
    df = pd.DataFrame(data=sorted_reversed, index=df.index, columns=df.columns)
    outpath = Path(tmp_dir, 'prices_pivoted_PY2009.csv')
    df.to_csv(outpath)

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
    # df2.to_csv(Path(tmp_dir, 'prices_pivoted_1980-2029.csv'))

    return df2


def pivot_prices(src, dst, years):
    tmp_dir = './temp'

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # First pivot historical prices
    dfs = []
    if 2009 in years:
        df_hist = pivot_historical_prices(src, tmp_dir)
        # hist_path = Path(tmp_dir, 'prices_pivoted_PY2009.csv')
        # df_hist = pd.read_csv(hist_path, parse_dates=True, index_col=0, header=0)
        df_hist.columns.name = 'Hour'
        dfs.append(df_hist)

    # future data
    if len([y for y in years if y != 2009]):
        prices_path = Path(src, 'NetLoad_for_UCM_2030_2060.csv')
        data = pd.read_csv(prices_path, header=0, skiprows=[1], index_col=0)

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
            # df.to_csv(Path(tmp_dir, 'prices_pivoted_PY{}.csv'.format(int(year))))
            dfs.append(df)

    df3 = pd.concat(dfs)

    outpath = os.path.join(dst, 'prices_pivoted_select_years.csv')
    df3.to_csv(outpath)


if __name__ == '__main__':
    dst = 'pivot_energy_prices/output'
    pivot_prices(dst)
