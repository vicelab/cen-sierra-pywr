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
parser.add_argument("-mp", "--multiprocessing", help="Use multiprocessing", default="none")
parser.add_argument("-s", "--start_year", help="Start year", type=int)
parser.add_argument("-e", "--end_year", help="End year", type=int)
parser.add_argument("-m", "--planning_months", help="Planning months", type=int)
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

data_path = os.environ.get('SIERRA_DATA_PATH')

if debug:
    planning_months = args.planning_months or 3
    climate_scenarios = ['Livneh']
    price_years = [2009]
    # climate_scenarios = ['CanESM2_rcp85']
    # price_years = [2060]
    start = '{}-10-01'.format(args.start_year or 2000)
    end = '{}-09-30'.format(args.end_year or 2002)
else:
    planning_months = args.planning_months or 12
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
    end=end,
    data_path=data_path
)

if multiprocessing == "none":  # serial processing for debugging
    for scenario in scenarios:
        print('Running: ', scenario)
        try:
            run_model(basin, scenario, price_years, **kwargs)
        except Exception as err:
            print("Failed: ", scenario)
            print(err)
            continue

elif multiprocessing == "slurm":
    run_model_partial = partial(run_model, **kwargs)
    time_start = time.time()
    output = Parallel(n_jobs=num_cores)(delayed(run_model_partial)(scenarios) for scenarios in range(number_of_simulations))
    output_size = np.matrix(output).shape
    time_end = time.time()

else:
    pool = mp.Pool(processes=mp.cpu_count() - 1)
    run_model_partial = partial(run_model, **kwargs)
    for scenario in scenarios:
        print('Adding ', scenario)
        pool.apply_async(run_model_partial, args=(basin, scenario))

    pool.close()
    pool.join()

print('done!')
