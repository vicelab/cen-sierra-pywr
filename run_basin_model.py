import os
import sys
import json
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from common.tests import test_planning_model, get_planning_dataframe
import pandas as pd

from utilities import simplify_network, prepare_planning_model, create_schematic

SECONDS_IN_DAY = 3600 * 24


def run_model(climate,
              basin=None,
              start=None, end=None,
              run_name="default",
              include_planning=False,
              simplify=True,
              use_multiprocessing=False,
              debug=False,
              planning_months=12,
              scenarios=None,
              show_progress=False,
              data_path=None):

    print("Running \"{}\" scenario for {} basin, {} climate".format(run_name, basin.upper(), climate.upper()))

    # Set up dates

    if start is None or end is None:
        if climate == 'Livneh':
            start_year = 1980
            end_year = 2012
        else:
            start_year = 2030
            end_year = 2060
        start = '{}-10-01'.format(start_year)
        end = '{}-09-30'.format(end_year)

    # ========================
    # Set up model environment
    # ========================

    here = os.path.dirname(os.path.realpath(__file__))
    os.chdir(here)

    root_dir = os.path.join(here, basin)
    temp_dir = os.path.join(root_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    bucket = 'openagua-networks'
    base_filename = 'pywr_model.json'
    model_filename_base = 'pywr_model_{}'.format(climate)
    model_filename = model_filename_base + '.json'

    base_path = os.path.join(root_dir, base_filename)
    model_path = os.path.join(temp_dir, model_filename)

    # first order of business: update file paths in json file
    with open(base_path) as f:
        base_model = json.load(f)

    # update model with scenarios, if any
    def update_model(scenario_path):
        if os.path.exists(scenario_path):
            with open(scenario_path) as f:
                scenario_model = json.load(f)
            for key in scenario_model.keys():
                if key in base_model:
                    if type(scenario_model[key]) == dict:
                        base_model[key].update(scenario_model[key])
                    elif key in ['scenarios', 'nodes']:
                        items = {item['name']: item for item in base_model.get(key, [])}
                        new_items = {item['name']: item for item in scenario_model[key]}
                        items.update(new_items)
                        base_model[key] = list(items.values())

    if scenarios is not None:
        for s in scenarios:
            # update from scenarios folder
            scenario_path = os.path.join(root_dir, '../scenarios/{}.json'.format(s))
            update_model(scenario_path)

    new_model_parts = {}
    for model_part in ['tables', 'parameters']:
        if model_part not in base_model:
            continue
        new_model_parts[model_part] = {}
        for pname, param in base_model[model_part].items():
            if 'observed' in pname.lower():
                continue
            url = param.get('url')
            if url:
                if data_path:
                    url = url.replace('../data', data_path)
                url = url.replace('Livneh', climate)
                param['url'] = url
            new_model_parts[model_part][pname] = param

    base_model.update(new_model_parts)
    base_model['timestepper']['start'] = start
    base_model['timestepper']['end'] = end
    with open(model_path, 'w') as f:
        json.dump(base_model, f, indent=4)

    # =========================================
    # Load and register global model parameters
    # =========================================

    # sys.path.insert(0, os.getcwd())
    policy_folder = 'parameters'
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = 'parameters.{policy_name}'.format(policy_name=policy_name)
        import_module(policy_module, policy_folder)

    # =========================================
    # Load and register custom model parameters
    # =========================================

    sys.path.insert(0, os.getcwd())
    policy_folder = os.path.join(basin, '_parameters')
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = '{basin}._parameters.{policy_name}'.format(basin=basin, policy_name=policy_name)
        import_module(policy_module, policy_folder)

    # import domains
    import_module('.domains', 'domains')
    if debug:
        print(" [*] Domains imported")

    # import custom policies
    try:
        import_module('{}.policies'.format(basin))
    except:
        pass

    # prepare the model files
    if simplify or include_planning:
        with open(model_path, 'r') as f:
            m = json.load(f)

    if simplify:
        # simplify model
        simplified_filename = model_filename_base + '_simplified.json'
        simplified_model_path = os.path.join(temp_dir, simplified_filename)

        m = simplify_network(m, basin=basin, climate=climate, delete_gauges=True, delete_observed=True,
                             delete_scenarios=debug)
        with open(simplified_model_path, 'w') as f:
            f.write(json.dumps(m, indent=4))
        create_schematic(basin, 'simplified')

        model_path = simplified_model_path

    # Area for testing monthly model
    save_results = debug and 'm' in debug
    planning_model = None
    df_planning = None

    if include_planning:

        print('Creating planning model (this may take a minute or two)')

        # create filenames, etc.
        monthly_filename = model_filename_base + '_monthly.json'
        planning_model_path = os.path.join(temp_dir, monthly_filename)

        prepare_planning_model(m, basin, climate, planning_model_path, steps=planning_months, debug=save_results,
                               remove_rim_dams=True)
        create_schematic(basin, 'monthly')

        # create pywr model
        try:
            planning_model = Model.load(planning_model_path, path=planning_model_path)
        except Exception as err:
            print("Planning model failed to load")
            print(err)
            raise

        # set model mode to planning
        planning_model.mode = 'planning'

        # set time steps
        # start = planning_model.timestepper.start
        end = planning_model.timestepper.end
        end -= relativedelta(months=planning_months)

        planning_model.setup()

        if debug == 'm':
            test_planning_model(planning_model, months=planning_months, save_results=save_results)
            return

    # ==================
    # Create daily model
    # ==================
    if debug:
        print(' [*] Loading daily model')
    from pywr.nodes import Storage
    from domains import Reservoir
    try:
        m = Model.load(model_path, path=model_path)
    except Exception as err:
        print(err)
        raise
    reservoirs = [n.name for n in m.nodes if type(n) in [Storage, Reservoir] and '(storage)' not in n.name]
    # piecewise_ifrs = [n.name for n in m.nodes if type(n) == Storage and '(storage)' not in n.name]
    m.setup()

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    # IMPORTANT: The following can be embedded into the scheduling model via
    # the 'before' and 'after' functions.
    days_to_omit = 0
    if include_planning:
        end = m.timestepper.end
        new_end = end + relativedelta(months=-planning_months)
        m.timestepper.end = new_end
    step = -1
    now = datetime.now()
    monthly_seconds = 0
    m.mode = 'scheduling'
    m.planning = None
    if include_planning:
        m.planning = planning_model
        m.planning.scheduling = m

    disable_progress_bar = not debug and not show_progress
    for date in tqdm(m.timestepper.datetime_index, ncols=60, disable=disable_progress_bar):
        step += 1
        try:

            # Step 1: run planning model
            if include_planning and date.day == 1:

                # update planning model
                m.planning.reset(start=date.to_timestamp())

                # run planning model (intial conditions are set within the model step)
                m.planning.step()

                if debug == 'dm' and save_results:
                    df_month = get_planning_dataframe(m.planning)
                    if df_planning is None:
                        df_planning = df_month
                    else:
                        df_planning = pd.concat([df_planning, df_month])

            # Step 2: run daily model
            m.step()
        except Exception as err:
            print('\nFailed at step {}'.format(date))
            print(err)
            raise

    if debug:
        total_seconds = (datetime.now() - now).total_seconds()
        print('Total run: {} seconds'.format(total_seconds))
        monthly_pct = monthly_seconds / total_seconds * 100
        print('Monthly overhead: {} seconds ({:02}% of total)'.format(monthly_seconds, monthly_pct))

    # save results to CSV
    results = m.to_dataframe()
    results.index.name = 'Date'
    scenario_name = climate
    scenario_names = [s.name for s in m.scenarios.scenarios]
    if not scenario_names:
        scenario_names = [0]
    results_path = os.path.join('./results', run_name, basin, scenario_name)
    if not debug:
        results_path = os.path.join(data_path, results_path)
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    if df_planning is not None:
        df_planning.to_csv(os.path.join(results_path, 'planning_debug.csv'))

    # results.columns = results.columns.droplevel(1)
    columns = {}
    # nodes_of_type = {}
    for c in results.columns:
        res_name, attr = c[0].split('/')
        if res_name in m.nodes:
            node = m.nodes[res_name]
            _type = type(node).__name__
        else:
            _type = 'Other'
        key = (_type, attr)
        if key in columns:
            columns[key].append(c)
        else:
            columns[key] = [c]
        # nodes_of_type[_type] = nodes_of_type.get(_type, []) + [node]
    for (_type, attr), cols in columns.items():
        if attr == 'elevation':
            unit = 'm'
        else:
            unit = 'mcm'
        tab_path = os.path.join(results_path, '{}_{}_{}'.format(_type, attr.title(), unit))
        df = results[cols]
        if scenario_names:
            new_cols = [tuple([col[0].split('/')[0]] + list(col[1:])) for col in cols]
            df.columns = pd.MultiIndex.from_tuples(new_cols)
            df.columns.names = ["node"] + scenario_names
        else:
            new_cols = [col[0].split('/')[0] for col in cols]
            df.columns = new_cols
        df.to_csv(tab_path + '.csv')

        if _type in ['Hydropower', 'PiecewiseHydropower'] and attr == 'flow':
            gen_df = df.copy()
            gen_path = os.path.join(results_path, '{}_Generation_MWh.csv'.format(_type))
            for c in df.columns:
                node = m.nodes[c[0]]
                gen_df *= node.head * 0.9 * 9.81 * 1000 / 1e6 * 24
                gen_df.to_csv(gen_path)
