import os
import multiprocessing as mp
from functools import partial
import argparse
from itertools import product
from run_basin_model import run_model

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basin", help="Basin to run")
parser.add_argument("-nk", "--network_key", help="Network key")
parser.add_argument("-d", "--debug", help="Debug ('m' or 'd' or 'dm')")
parser.add_argument("-p", "--include_planning", help="Include planning model", action='store_true')
parser.add_argument("-n", "--run_name", help="Run name")
parser.add_argument("-mp", "--multiprocessing", help="Use multiprocessing", action='store_true')
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')
debug = args.debug
include_planning = args.include_planning
multiprocessing = args.multiprocessing

gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
# gcms = ['HadGEM2-ES', 'MIROC5']
rcps = ['45', '85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]

start = None
end = None
if debug:
    planning_months = 6
    climate_scenarios = ['Livneh']
    price_years = [2009, 2060]
    # climate_scenarios = ['CanESM2_rcp85']
    # price_years = [2060]
    start = '2003-10-01'
    end = '2005-09-30'
else:
    planning_months = 12
    climate_scenarios = ['Livneh'] + gcm_rcps
    # climate_scenarios = ['HadGEM2-ES_rcp85']  # + gcm_rcps
    price_years = [2009, 2060]
    # start = '2003-10-01'
    # end = '2005-09-30'

scenarios = climate_scenarios

kwargs = dict(
    run_name=args.run_name,
    include_planning=include_planning,
    debug=debug,
    planning_months=planning_months,
    use_multiprocessing=multiprocessing,
    start=start,
    end=end
)

if not multiprocessing:  # serial processing for debugging
    for scenario in scenarios:
        print('Running: ', scenario)
        try:
            run_model(basin, scenario, price_years, **kwargs)
        except Exception as err:
            print("Failed: ", scenario)
            print(err)
            continue

else:
    pool = mp.Pool(processes=mp.cpu_count() - 1)
    run_model_partial = partial(run_model, **kwargs)
    for scenario in scenarios:
        print('Adding ', scenario)
        pool.apply_async(run_model_partial, args=(basin, scenario))

    pool.close()
    pool.join()

print('done!')
