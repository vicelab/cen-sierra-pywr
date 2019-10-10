import os
import sys
import json
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm


def load_model(root_dir, model_path, bucket=None, network_key=None, check_graph=False):
    os.chdir(root_dir)

    # needed when loading JSON file
    root_path = 's3://{}/{}/'.format(bucket, network_key)
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

    # Step 2: Load and run daily model
    ret = Model.load(model_path, path=model_path)
    return ret


def create_planning_model(path, steps=12):
    with open(path) as f:
        m = json.load(f)

    all_steps = range(steps)

    new_nodes = []
    new_edges = []
    new_parameters = {}
    new_recorders = []

    gauges = {}

    for node in m['nodes']:
        old_name = node['name']
        node_type = node['type']
        if node_type == 'RiverGauge':
            gauges[old_name] = [0, 0]
            continue
        for step in all_steps:
            t = step + 1
            new_node = node.copy()
            new_node_name = '{}/{}'.format(old_name, t)
            next_node_name = '{}/{}'.format(old_name, t + 1)
            new_node['name'] = new_node_name

            if node_type == 'Catchment' and 'flow' in node:
                new_node['flow'] += '/{}'.format(t)

            if node_type == 'PiecewiseHydropower':
                new_node['max_flow'] = ['{}/{}'.format(c, t) for c in node['max_flow']]
                new_node['cost'] = ['{}/{}'.format(c, t) for c in node['cost']]

            new_nodes.append(new_node)

            if t < steps and node['type'] == 'Storage':
                new_edges.append([new_node_name, next_node_name])

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
        if len(parts) == 3:
            resource_class, resource_name, attribute = parts
            if attribute in ['Observed Flow', 'Observed Storage']:
                continue

            if attribute in ['Runoff', 'Water Demand']:
                for step in all_steps:
                    t = step + 1
                    new_param_name = '{}/{}'.format(param_name, t)
                    new_param = param.copy()
                    if attribute == 'Runoff':
                        new_param['column'] = '{:02}'.format(t)
                    new_parameters[new_param_name] = new_param

                continue

        new_parameters[param_name] = param

    for recorder_name in m['recorders']:
        recorder = m['recorders'][recorder_name]
        if 'node' in recorder:
            if recorder['node'] in gauges:
                continue
            recorder['node'] += '/0'  # record just the first time step results
            new_recorders.append(recorder)

    m['nodes'] = new_nodes
    m['edges'] = new_edges
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    root, filename = os.path.split(path)
    base, ext = os.path.splitext(filename)
    new_filename = '{}_monthly'.format(base) + ext
    new_path = os.path.join(root, new_filename)
    with open(new_path, 'w') as f:
        json.dump(m, f, indent=4)
    return


def run_model(basin, network_key):
    root_dir = os.path.join(os.getcwd(), basin)
    bucket = 'openagua-networks'
    model_path = os.path.join(root_dir, 'pywr_model.json')

    # model = load_model(root_dir, model_path, bucket=bucket, network_key=network_key)

    # create monthly model
    planning_model = create_planning_model(model_path)

    # initialize daily model
    # setattr(model, 'mode', 'scheduling')
    model.setup()

    # initialize monthly model
    setattr(planning_model, 'mode', 'planning')

    timesteps = range(len(model.timestepper))
    step = None

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    for step in tqdm(timesteps, ncols=80):
        try:
            model.step()
        except Exception as err:
            print('\nFailed at step {}'.format(model.timestepper.current))
            print(err)
            # continue
            break

    # save results to CSV

    results = model.to_dataframe()
    results.columns = results.columns.droplevel(1)
    results_path = './results'
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
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')

run_model(basin, network_key)

print('done!')
