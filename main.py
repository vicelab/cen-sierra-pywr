import os
import json
import argparse
from itertools import product
from run_basin_model import run_model
from functools import partial

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basin", help="Basin to run")
parser.add_argument("-nk", "--network_key", help="Network key")
parser.add_argument("-d", "--debug", help="Debug ('m' or 'd' or 'dm')")
parser.add_argument("-p", "--include_planning", help="Include planning model", action='store_true')
parser.add_argument("-sc", "--scenario_set", help="Scenario set")
parser.add_argument("-mp", "--multiprocessing", help="Multiprocessing protocol (omit for none)")
parser.add_argument("-s", "--start_year", help="Start year", type=int)
parser.add_argument("-e", "--end_year", help="End year", type=int)
parser.add_argument("-m", "--planning_months", help="Planning months", type=int)
parser.add_argument("-n", "--run_name", help="Run name")
parser.add_argument("-pb", "--progress_bar", help="Show progress bar", action='store_true')
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')
debug = args.debug
include_planning = args.include_planning
multiprocessing = args.multiprocessing

data_path = os.environ.get('SIERRA_DATA_PATH')

start = None
end = None
scenarios = []

run_name = args.run_name or 'baseline'
climate_scenarios = ['Livneh']

if debug:
    planning_months = args.planning_months or 3
    start = '{}-10-01'.format(args.start_year or 2000)
    end = '{}-09-30'.format(args.end_year or 2002)
    run_name = 'development'
else:
    planning_months = args.planning_months or 12

if args.start_year:
    start = '{}-10-01'.format(args.start_year)
if args.end_year:
    end = '{}-09-30'.format(args.end_year)

if args.scenario_set:
    with open("./scenario_sets.json") as f:
        scenario_sets = json.load(f)

    scenario_set_definition = scenario_sets.get(args.scenario_set)
    if not scenario_set_definition:
        raise Exception("Scenario set {} not defined in scenario_sets.json".format(args.scenario_set))
    scenarios = scenario_set_definition.get('scenarios', [])
    climates = scenario_set_definition.get('climates', [])
    run_name = scenario_set_definition['name']
    if climates:
        climate_scenarios = []
        if 'historical' in climates:
            climate_scenarios = ['Livneh']
        if 'gcms' in climates:
            gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
            # gcms = ['HadGEM2-ES', 'MIROC5']
            # rcps = ['45', '85']
            rcps = ['85']
            gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]
            climate_scenarios += gcm_rcps

kwargs = dict(
    basin=basin,
    run_name=run_name,
    include_planning=include_planning,
    debug=debug,
    planning_months=planning_months,
    use_multiprocessing=multiprocessing is not None,
    start=start,
    end=end,
    data_path=data_path,
    scenarios=scenarios,
    show_progress=args.progress_bar
)

if not multiprocessing:  # serial processing for debugging
    for climate in climate_scenarios:
        print('Running: ', climate)
        try:
            run_model(climate, **kwargs)
        except Exception as err:
            print("Failed: ", climate)
            print(err)
            continue

else:
    import multiprocessing as mp

    num_cores = mp.cpu_count() - 1
    run_partial = partial(run_model, **kwargs)

    if multiprocessing == 'joblib':
        from joblib import Parallel, delayed
        output = Parallel(n_jobs=num_cores)(delayed(run_partial)(climate) for climate in climate_scenarios)

    else:
        pool = mp.Pool(processes=num_cores)
        for climate in climate_scenarios:
            print('Adding ', climate)
            pool.apply_async(run_partial, args=(climate))

        pool.close()
        pool.join()

print('done!')
