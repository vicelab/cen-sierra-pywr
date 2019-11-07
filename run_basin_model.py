import os
import sys
import json
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm


def setup_model(root_dir, model_path, bucket=None, network_key=None, check_graph=False):
    os.chdir(root_dir)

    # needed when loading JSON file
    # root_path = 's3://{}/{}/'.format(bucket, network_key)
    root_path = '../data'
    os.environ['ROOT_S3_PATH'] = root_path

    # Step 1: Load and register policies for daily model
    sys.path.insert(0, os.getcwd())
    policy_folder = '_parameters'
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = '.{policy_name}'.format(policy_name=policy_name)
        # package = '.{}'.format(policy_folder)
        import_module(policy_module, policy_folder)

    modules = [
        # ('.IFRS', 'policies'),
        ('.domains', 'domains')
    ]
    for name, package in modules:
        try:
            import_module(name, package)
        except Exception as err:
            print(' [-] WARNING: {} could not be imported from {}'.format(name, package))
            print(type(err))
            print(err)

    return


def prepare_planning_model(path, outpath, steps=12):
    with open(path) as f:
        m = json.load(f)

    # update time step
    # m['timestepper']['end'] = m['timestepper']['start']
    # m['timestepper']['timestep'] = 'M'
    # m['metadata']['title'] += ' - planning'

    all_steps = range(steps)

    new_nodes = []
    new_edges = []
    new_parameters = {}
    new_recorders = {}

    gauges = {}

    parameters_to_expand = []
    black_list = ['min_volume', 'max_volume']

    for node in m['nodes']:
        old_name = node['name']
        node_type = node['type']
        if node_type == 'RiverGauge':
            gauges[old_name] = [0, 0]
            continue

        for key, value in node.items():
            if key in black_list:
                continue
            if type(value) == str and value in m['parameters']:
                if value not in parameters_to_expand:
                    parameters_to_expand.append(value)

        res_class = 'network'
        res_name = 'network'
        name_parts = old_name.replace(' [', '/').replace(']', '').split('/')
        if len(name_parts) > 1 and name_parts[1] in ['node', 'link']:
            res_name, res_class = name_parts

        for step in all_steps:
            t = step + 1
            new_node = node.copy()
            new_res_name = '{}/{}'.format(old_name, t)
            next_res_name = '{}/{}'.format(old_name, t + 1)
            new_node['name'] = new_res_name

            month = '/{}'.format(t)

            for key, value in node.items():
                if type(value) == str and value in m['parameters']:
                    if key not in black_list:
                        new_node[key] += month

                elif type(value) == list:
                    new_values = []
                    for v in value:
                        if type(v) == str:
                            if v not in parameters_to_expand:
                                parameters_to_expand.append(v)
                            parts = v.split('/')
                            if len(parts) == 3:
                                new_values.append(v + month)
                            elif len(parts) == 4:
                                attr = parts[-2]
                                block = parts[-1]
                                new_v = '{}/{}/{}/{}/{}'.format(res_class, res_name, attr, t, block)
                                new_values.append(new_v)
                            else:
                                new_values.append(v)
                        else:
                            new_values.append(v)
                    new_node[key] = new_values

            new_nodes.append(new_node)

            if t < steps and node['type'] == 'Storage':
                new_edges.append([new_res_name, next_res_name])

    edges_temp = []
    for n1, n2 in m['edges']:
        if n1 in gauges:
            gauges[n1][1] = n2
        elif n2 in gauges:
            gauges[n2][0] = n1
        else:
            edges_temp.append([n1, n2])
    edges_temp += list(gauges.values())

    for n1, n2 in edges_temp:
        # for n1, n2 in m['edges']:
        for step in all_steps:
            t = step + 1
            new_edges.append(['{}/{}'.format(n1, t), '{}/{}'.format(n2, t)])

    for param_name in m['parameters']:
        parts = param_name.split('/')
        param = m['parameters'][param_name]
        res_class = None
        res_name = None
        attribute = None
        block = None
        if len(parts) == 3:
            res_class, res_name, attribute = parts
        elif len(parts) == 4:
            res_class, res_name, attribute, block = parts
            block = int(block)

        if attribute in ['Observed Flow', 'Observed Storage']:
            continue

        if param_name in parameters_to_expand or 'node' in param:
            for step in all_steps:
                t = step + 1
                new_param_name = '{}/{}/{}/{}'.format(res_class, res_name, attribute, t)
                if block:
                    new_param_name += '/{}'.format(block)
                new_param = param.copy()
                if attribute == 'Runoff':
                    new_param['column'] = '{:02}'.format(t)
                    new_param['url'] = new_param['url'].replace('/runoff/', '/runoff_monthly_forecasts/')
                if 'node' in param:
                    new_param['node'] += '/{}'.format(t)
                if 'storage_node' in param:
                    new_param['storage_node'] += '/{}'.format(t)

                new_parameters[new_param_name] = new_param
            continue

        new_parameters[param_name] = param

    for recorder_name in m['recorders']:
        recorder = m['recorders'][recorder_name]
        if 'node' in recorder:
            if recorder['node'] in gauges:
                continue
            recorder['node'] += '/1'  # record just the first time step results
            new_recorders[recorder_name] = recorder

    m['nodes'] = new_nodes
    m['edges'] = new_edges
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    with open(outpath, 'w') as f:
        json.dump(m, f, indent=4)
    return


def create_planning_model(model_path):
    root, filename = os.path.split(model_path)
    base, ext = os.path.splitext(filename)
    new_filename = '{}_monthly'.format(base) + ext
    monthly_model_path = os.path.join(root, new_filename)
    prepare_planning_model(model_path, monthly_model_path)
    # monthly_model = load_model(root_dir, monthly_model_path, bucket=bucket, network_key=network_key, mode='planning')
    monthly_model = Model.load(monthly_model_path, path=monthly_model_path)
    setattr(monthly_model, 'mode', 'planning')
    monthly_model.setup()
    print('Monthly model setup complete')
    return monthly_model


def run_model(basin, network_key, run_type='normal'):
    # ========================
    # Set up model environment
    # ========================

    basin = basin.strip()
    run_type = run_type.strip()

    if run_type == 'calibrate':
        root_dir = os.path.join(os.path.dirname(os.getcwd()), basin)
    else:
        root_dir = os.path.join(os.getcwd(), basin)

    bucket = 'openagua-networks'
    model_path = os.path.join(root_dir, 'pywr_model.json')

    # setup_model(root_dir, model_path, bucket=bucket, network_key=network_key)
    os.chdir(root_dir)

    # needed when loading JSON file
    # root_path = 's3://{}/{}/'.format(bucket, network_key)
    root_path = '../data'
    os.environ['ROOT_S3_PATH'] = root_path

    # =========================================
    # Load and register custom model parameters
    # =========================================

    sys.path.insert(0, os.getcwd())
    policy_folder = '_parameters'
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = '.{policy_name}'.format(policy_name=policy_name)
        # package = '.{}'.format(policy_folder)
        import_module(policy_module, policy_folder)

    modules = [
        ('.IFRS', 'policies'),
        ('.domains', 'domains')
    ]
    for name, package in modules:
        try:
            import_module(name, package)
        except Exception as err:
            print(' [-] WARNING: {} could not be imported from {}'.format(name, package))
            print(type(err))
            print(err)

    # ==================
    # Create daily model
    # ==================
    include_monthly = False
    daily_model = Model.load(model_path, path=model_path)
    print('Daily model loaded')
    daily_model.setup()
    print('Daily model setup completed')
    # =====================
    # Create planning model
    # =====================

    # create and initialize monthly model
    if include_monthly:
        monthly_model = create_planning_model(model_path)

    timesteps = range(len(daily_model.timestepper))

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    for step in tqdm(timesteps, ncols=80):

        today = daily_model.timestepper.current if step else daily_model.timestepper.start

        try:

            # Step 1: run planning model & update daily model

            if include_monthly and today.day == 1:

                # Step 1a: update planning model

                # ...update time steps
                monthly_model.timestepper.start = today
                monthly_model.timestepper.end = today

                # ...update initial conditions (not needed for the first step)
                if step > 0:
                    for node in monthly_model.nodes:
                        if node['type'] != 'Storage':
                            continue

                        node['initial_volume'] = daily_model.node[node['name']].volume

                # Step 1b: run planning model
                print('Running planning model')
                monthly_model.step()  # redundant with run, since only one timestep

                # Step 1c: update daily model with planning model results
                print('Updating daily model')

            # Step 3: run daily model
            daily_model.step()
        except Exception as err:
            print('\nFailed at step {}'.format(today))
            print(err)
            # continue
            break

    # save results to CSV

    results = daily_model.to_dataframe()
    results_path = './results'
    results.columns = results.columns.droplevel(1)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    results.to_csv(os.path.join(results_path, 'system.csv'))
    attributes = {}
    for c in results.columns:
        attribute = c.split('/')[-1]
        if attribute in attributes:
            attributes[attribute].append(c)
        else:
            attributes[attribute] = [c]
    for attribute in attributes:
        path = os.path.join(results_path, '{}.csv'.format(attribute))
        df = results[attributes[attribute]]
        df.columns = [c.split('/')[-2] for c in df.columns]
        df.to_csv(path)

        if attribute == 'flow':
            df2 = df[[c for c in df.columns if c[-3:] == ' PH']]
            path2 = os.path.join(results_path, 'powerhouse flow.csv')
            df2.to_csv(path2)


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basin", help="Basin to run")
parser.add_argument("-nk", "--network_key", help="Network key")
parser.add_argument("-t", "--model_type", help="Model Type")
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')
run_type = args.model_type

run_model(basin, network_key, run_type)

print('done!')
