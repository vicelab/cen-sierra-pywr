import os
from preprocessing.energy_prices import linearize_prices
from preprocessing.energy_prices import pivot_prices

rootdir = os.environ['SIERRA_DATA_PATH']
outdir = os.path.join(rootdir, 'common', 'energy prices')

# Linearize energy prices for planning model
steps = ['daily', 'monthly']
periods = ['historical', 'future']
linearize_prices(steps, periods, outdir)

# Pivot energy prices for scheduling model
pivot_prices(outdir)
