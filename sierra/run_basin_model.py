import os
import sys
import json
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sierra.common.tests import get_planning_dataframe
import pandas as pd
import traceback
from sierra.utilities import simplify_network, prepare_planning_model, save_model_results, create_schematic
from loguru import logger
from graphviz import ExecutableNotFound

SECONDS_IN_DAY = 3600 * 24


def run_model(*args, **kwargs):
    climate = args[0]
    basin = args[1]
    run_name = kwargs['run_name']

    logger_name = '{}-{}-{}.log'.format(run_name, basin, climate.replace('/', '_'))
    logs_dir = os.path.join('.', 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    logger_path = os.path.join(logs_dir, logger_name)
    if os.path.exists(logger_path):
        try:
            os.remove(logger_path)
            logger.add(logger_path)
        except:
            logger.warning('Failed to remove log file {}'.format(logger_path))
    else:
        logger.add(logger_path)

    try:
        _run_model(*args, **kwargs)
    except Exception as err:
        logger.exception(err)
        logger.error("Failed")


def _run_model(climate,
               basin,
               start=None, end=None,
               years=None,
               run_name="default",
               include_planning=False,
               simplify=True,
               use_multiprocessing=False,
               debug=False,
               blocks=8,
               planning_months=12,
               scenarios=None,
               show_progress=False,
               data_path=None,
               file_suffix=None
               ):
    logger.info("Running \"{}\" scenario for {} basin, {} climate".format(run_name, basin.upper(), climate.upper()))

    climate_set, climate_scenario = climate.split('/')

    if debug:
        from sierra.utilities import check_nan
        basin_path = os.path.join(data_path, basin.replace('_', ' ').title() + ' River')
        total_nan = check_nan(basin_path, climate)

        try:
            assert (total_nan == 0)
            logger.info('No NaNs found in data files')
        except AssertionError:
            logger.warning('{} NaNs found in data files.'.format(total_nan))

    # if debug:
    #     from sierra import create_schematic

    # Some adjustments
    if basin in ['merced', 'tuolumne']:
        include_planning = False

    # Set up dates

    if start is None or end is None:
        # TODO: get start and end years from outside, not hard coded
        if climate_scenario == 'Livneh':
            start_year = 1950
            end_year = 2012
        elif climate_set == 'gcms':
            start_year = 2030
            end_year = 2060
        elif climate_set == 'sequences':
            # name format is N01_S01, where N01 refers to the number of drought years
            # the total number of years is 1 + N + 2 (1 year at the end as a buffer)
            N = int(climate_scenario.split('Y')[1].split('_')[0])
            start_year = 2000
            end_year = start_year + N
        else:
            raise Exception("Climate scenario unknown")
        start = '{}-10-01'.format(start_year)
        end = '{}-09-30'.format(end_year)

    # ========================
    # Set up model environment
    # ========================

    here = os.path.dirname(os.path.realpath(__file__))
    os.chdir(here)

    root_dir = os.path.join(here, 'models', basin)
    temp_dir = os.path.join(root_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    bucket = 'openagua-networks'
    base_filename = 'pywr_model.json'
    model_filename_base = 'pywr_model_{}'.format(climate_scenario)
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
            for key, scenario_items in scenario_model.items():
                if key in base_model:
                    if type(scenario_items) == dict:
                        base_model[key].update(scenario_items)
                    else:
                        base_model[key].extend(scenario_items)
                elif key in ['scenarios', 'nodes']:
                    items = {item['name']: item for item in base_model.get(key, [])}
                    new_items = {item['name']: item for item in scenario_items}
                    items.update(new_items)
                    base_model[key] = list(items.values())
        else:
            raise Exception('Scenario path {} does not exist.'.format(scenario_path))

    if scenarios is not None:
        for s in scenarios:
            # update from scenarios folder
            scenario_path = os.path.join(data_path, 'metadata', 'scenario_definitions', '{}.json'.format(s))
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
                url = url.replace('historical/Livneh', climate)
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
        policy_module = 'sierra.parameters.{policy_name}'.format(policy_name=policy_name)
        import_module(policy_module, policy_folder)

    # =========================================
    # Load and register custom model parameters
    # =========================================

    sys.path.insert(0, os.getcwd())
    policy_folder = os.path.join('models', basin, '_parameters')
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = 'models.{basin}._parameters.{policy_name}'.format(basin=basin, policy_name=policy_name)
        import_module(policy_module, policy_folder)

    # import domains
    import_module('.domains', 'domains')
    if debug:
        logger.info("Domains imported")

    # import custom policies
    try:
        import_module('{}.policies'.format(basin))
    except:
        pass

    # =========================================
    # Load and register custom model recorders
    # =========================================

    from recorders.hydropower import HydropowerEnergyRecorder
    HydropowerEnergyRecorder.register()

    # prepare the model files
    if simplify or include_planning:
        with open(model_path, 'r') as f:
            model_json = json.load(f)

    if simplify:
        # simplify model
        simplified_filename = model_filename_base + '_simplified.json'
        simplified_model_path = os.path.join(temp_dir, simplified_filename)

        model_json = simplify_network(model_json, basin=basin, climate=climate, delete_gauges=True,
                                      delete_observed=True)
        with open(simplified_model_path, 'w') as f:
            f.write(json.dumps(model_json, indent=4))

        if debug:
            try:
                create_schematic(basin, 'simplified')
            except FileNotFoundError as err:
                logger.warning('Could not create schematic from Livneh model.')
            except ExecutableNotFound:
                logger.warning('Could not create daily schematic from Livneh model.')

        model_path = simplified_model_path

    # Area for testing monthly model
    save_results = debug
    planning_model = None
    df_planning = None

    if include_planning:

        logger.info('Creating planning model (this may take a minute or two)')

        # create filenames, etc.
        monthly_filename = model_filename_base + '_monthly.json'
        planning_model_path = os.path.join(temp_dir, monthly_filename)

        prepare_planning_model(model_json, basin, climate, planning_model_path,
                               steps=planning_months, blocks=blocks, debug=debug, remove_rim_dams=True)

        if debug:
            try:
                create_schematic(basin, 'monthly')
            except ExecutableNotFound:
                logger.warning('Graphviz executable not found. Monthly schematic not created.')

        # create pywr model
        try:
            planning_model = Model.load(planning_model_path, path=planning_model_path)
        except Exception as err:
            logger.error("Planning model failed to load")
            # logger.error(err)
            raise

        # set model mode to planning
        planning_model.mode = 'planning'
        planning_model.blocks = {}

        # set time steps
        # start = planning_model.timestepper.start
        end = planning_model.timestepper.end
        end -= relativedelta(months=planning_months)

        planning_model.setup()

        # if debug == 'm':
        #     test_planning_model(planning_model, months=planning_months, save_results=save_results)
        #     return

    # ==================
    # Create daily model
    # ==================
    logger.info('Loading daily model')
    try:
        model = Model.load(model_path, path=model_path)
    except Exception as err:
        logger.error(err)
        raise

    model.blocks = {}
    model.setup()

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    # IMPORTANT: The following can be embedded into the scheduling model via
    # the 'before' and 'after' functions.
    days_to_omit = 0
    if include_planning:
        end = model.timestepper.end
        new_end = end + relativedelta(months=-planning_months)
        model.timestepper.end = new_end
    step = -1
    now = datetime.now()
    monthly_seconds = 0
    model.mode = 'scheduling'
    model.planning = None
    if include_planning:
        model.planning = planning_model
        model.planning.scheduling = model

    disable_progress_bar = not debug and not show_progress
    n_timesteps = len(model.timestepper.datetime_index)
    for date in tqdm(model.timestepper.datetime_index, ncols=60, disable=disable_progress_bar):
        step += 1
        if disable_progress_bar and date.month == 9 and date.day == 30:
            logger.info('{}% complete (finished year {})'.format(round(step / n_timesteps * 100), date.year))
        try:

            # Step 1: run planning model
            if include_planning and date.day == 1:

                # update planning model
                model.planning.reset(start=date.to_timestamp())

                # run planning model (intial conditions are set within the model step)
                model.planning.step()

                if debug and save_results:
                    df_month = get_planning_dataframe(model.planning)
                    if df_planning is None:
                        df_planning = df_month
                    else:
                        df_planning = pd.concat([df_planning, df_month])

            # Step 2: run daily model
            model.step()
        except Exception as err:
            traceback.print_exc()
            logger.error('Failed at step {}'.format(date))
            raise

    if debug:
        total_seconds = (datetime.now() - now).total_seconds()
        logger.debug('Total run: {} seconds'.format(total_seconds))
        monthly_pct = monthly_seconds / total_seconds * 100
        logger.debug('Monthly overhead: {} seconds ({:02}% of total)'.format(monthly_seconds, monthly_pct))

    # save results to CSV
    # results_path = os.path.join('./results', run_name, basin, climate)
    if debug:
        base_results_path = '../results'
    else:
        base_results_path = os.environ.get('SIERRA_RESULTS_PATH', '../results')

    suffix = ' - {}'.format(file_suffix) if file_suffix else ''
    run_folder = run_name + suffix
    results_path = os.path.join(base_results_path, run_folder, basin, climate)
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    if debug and save_results and df_planning is not None:
        df_planning_path = os.path.join(results_path, 'planning_model_results.csv')
        df_planning.to_csv(df_planning_path)

    save_model_results(model, results_path, file_suffix, disaggregate=False, debug=debug)
