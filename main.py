import os
import json
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
parser.add_argument("-sc", "--scenario_set", help="Scenario set")
parser.add_argument("-mp", "--multiprocessing", help="Use multiprocessing", action='store_true')
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

start = None
end = None
scenarios = []

if debug:
    planning_months = args.planning_months or 3
    climate_scenarios = ['Livneh']
    start = '{}-10-01'.format(args.start_year or 2000)
    end = '{}-09-30'.format(args.end_year or 2002)

elif not args.scenario_set:
    raise Exception("No scenario set specified")

else:
    planning_months = args.planning_months or 12
    climate_scenarios = ['Livneh'] + gcm_rcps

with open("./scenario_sets.json") as f:
    scenario_sets = json.load(f)
    scenario_set_definition = scenario_sets.get(args.scenario_set)
    if not scenario_set_definition:
        raise Exception("Scenario set not defined in scenario_sets.json")
    scenarios = scenario_set_definition.get('scenarios', [])

kwargs = dict(
    run_name=args.run_name,
    include_planning=include_planning,
    debug=debug,
    planning_months=planning_months,
    use_multiprocessing=multiprocessing,
    start=start,
    end=end,
    data_path=data_path,
    scenarios=scenarios
)

if not multiprocessing:  # serial processing for debugging
    for climate_scenario in climate_scenarios:
        print('Running: ', climate_scenario)
        try:
            run_model(basin, climate_scenario, **kwargs)
        except Exception as err:
            print("Failed: ", climate_scenario)
            print(err)
            continue

else:
    pool = mp.Pool(processes=mp.cpu_count() - 1)
    run_model_partial = partial(run_model, **kwargs)
    for climate_scenario in climate_scenarios:
        print('Adding ', climate_scenario)
        pool.apply_async(run_model_partial, args=(basin, climate_scenario))

    pool.close()
    pool.join()

print('done!')
