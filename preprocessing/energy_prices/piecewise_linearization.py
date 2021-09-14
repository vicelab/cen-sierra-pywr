import os
from os import path
from os.path import join
import datetime as dt
import pwlf
import pandas as pd
import numpy as np
from tqdm import tqdm
from loguru import logger


def linearize_values(values, n_pieces, method='fit'):
    y = np.array(values)
    x = range(1, len(y) + 1)

    lf = pwlf.PiecewiseLinFit(x, y, degree=0)
    if method == 'fit':
        res = lf.fit(n_pieces)
    elif method == 'fitfast':
        res = lf.fitfast(n_pieces, pop=100)
    else:
        raise Exception('no valid method provided')

    blocks_cum = res[1:] / max(res)
    pw_blocks = np.array([blocks_cum[0]] + list(blocks_cum[1:] - blocks_cum[:-1])).round(3)
    pw_values = np.array([sum(lf.beta[:n + 1]) for n in range(n_pieces)]).round(3)

    return pw_blocks, pw_values


def linearize_prices(step, n_pieces, method='fit', years=None, data=None, input_dir=None, output_dir='./output'):
    logger.info('Processing step={}, n_pieces={}, method={}'.format(step, n_pieces, method))

    if not data:
        if not input_dir:
            input_dir = path.split(path.realpath(__file__))[0]
        historical_path = join(input_dir, 'Historical Net Load and Electricity Price.csv')
        future_path = join(input_dir, 'NetLoad_for_UCM_2030_2060.csv')
        df_2009 = pd.read_csv(historical_path, index_col=0, header=0, skiprows=[0],
                              usecols=[0, 2], names=['Date', '2009'])
        df_future = pd.read_csv(future_path, index_col=0, header=0, skiprows=[1])
        df = pd.concat([df_2009, df_future], axis=1)
    else:
        df = data

    dates = []
    blocks_all = []
    prices_all = []

    years = years or [int(y) for y in df.columns]

    for year in years:

        logger.info('year = {}'.format(year))

        # set the index
        starttime = dt.datetime(int(year), 1, 1)
        datetimes = [starttime + dt.timedelta(hours=h - 1) for h in df.index]
        year_prices = df[str(year)]
        year_prices.index = pd.DatetimeIndex(datetimes, freq='H')

        if step == 'monthly':
            periods = range(1, 13)
            year_dates = [dt.date(year, month, 1) for month in periods]
        elif step == 'daily':
            year_dates = pd.date_range(start=dt.date(year, 1, 1), end=dt.date(year, 12, 31))
        else:
            raise Exception('invalid step')

        dates.extend(year_dates)

        for date in tqdm(year_dates, ncols=160):

            if step == 'monthly':
                prices = year_prices[year_prices.index.month == date.month]
            elif step == 'daily':
                prices = year_prices[year_prices.index.month == date.month]
                prices = prices[prices.index.day == date.day]
            sorted_values = sorted(prices.values)
            sorted_values.reverse()

            blocks, prices = linearize_values(sorted_values, n_pieces, method=method)

            blocks_all.append(blocks)
            prices_all.append(prices)

    # Save data
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    block_labels = range(1, n_pieces + 1)

    def save_data(data, filename):
        df = pd.DataFrame(index=dates[:len(data)], data=data, columns=block_labels)
        df.index.name = 'Date'
        output_path = join(output_dir, '{}.csv'.format(filename.format(step=step)))
        df.to_csv(output_path)

    save_data(blocks_all, 'piecewise_blocks_{step}')
    save_data(prices_all, 'piecewise_prices_DpMWh_{step}')

    return


if __name__ == '__main__':

    method = 'fitfast'
    step = 'monthly'
    for n_pieces in range(2, 11):
        output_dir = join('./output/method={} step={} blocks={}'.format(method, step, n_pieces))
        linearize_prices(step, n_pieces, method=method)

    linearize_prices('daily', 4)
