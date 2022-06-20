import os
import argparse
from energy_prices import linearize_prices, pivot_prices


def preprocess_prices(years):
    rootdir = os.environ['SIERRA_DATA_PATH']
    outdir = os.path.join(rootdir, 'common', 'energy prices')
    input_dir = os.path.join('../data/electricity_prices')

    # Linearize energy prices for planning model
    n_pieces = 5
    method = 'fit'  # options are 'fit' and 'fitfast' (see pwlf documentation)
    for step in ['daily', 'monthly']:
        linearize_prices(step, n_pieces, method=method, years=years, output_dir=outdir, input_dir=input_dir)

    # Pivot energy prices for scheduling model
    pivot_prices(input_dir, outdir, years)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--year", help="Year to preprocess.", type=int)
    args = parser.parse_args()
    years = [args.year] if args.year else [2009, 2030, 2045, 2060]
    preprocess_prices(years)
