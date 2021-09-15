import os
from preprocessing.energy_prices import linearize_prices
from preprocessing.energy_prices import pivot_prices

rootdir = os.environ['SIERRA_DATA_PATH']
outdir = os.path.join(rootdir, 'common', 'energy prices')

# Linearize energy prices for planning model
n_pieces = 5
method = 'fit'  # options are 'fit' and 'fitfast' (see pwlf documentation)
years = [2009, 2030, 2045, 2060]
linearize_prices('monthly', n_pieces, method=method, years=years, output_dir=outdir)
linearize_prices('daily', 4, method=method, years=years, output_dir=outdir)

# Pivot energy prices for scheduling model
pivot_prices(outdir)
