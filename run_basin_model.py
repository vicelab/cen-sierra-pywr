import os
import sys
import json
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


# from pandas import ExcelWriter


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


def simplify_network(m, delete_gauges=False):
    # simplify the network
    mission_complete = False
    obsolete_gauges = []

    while not mission_complete:
        mission_complete = True
        up_nodes = []
        down_nodes = []
        up_edges = {}
        down_edges = {}
        for edge in m['edges']:
            a, b = edge
            up_nodes.append(a)
            down_nodes.append(b)
            down_edges[a] = edge
            up_edges[b] = [edge] if b not in up_edges else up_edges[b] + [edge]

        obsolete_nodes = []
        obsolete_edges = []
        new_edges = []

        for node in m['nodes']:
            # is the node a simple link? if so, we might be able to remove it
            node_name = node['name']
            node_type = node['type'].lower()
            metadata = json.loads(node.get('comment', '{}'))
            keys_set = set(node.keys())
            if keys_set in [{'name', 'type'}, {'name', 'type', 'comment'}] and not metadata.get('keep') \
                    or delete_gauges and node_type == 'rivergauge' \
                    or node_type == 'storage' and not node.get('max_volume'):
                if delete_gauges and node_type == 'rivergauge':
                    obsolete_gauges.append(node_name)
                if down_nodes.count(node_name) == 0:
                    # upstream-most node
                    obsolete_nodes.append(node_name)
                    obsolete_edges.append(down_edges[node_name])
                    mission_complete = False
                    break
                elif up_nodes.count(node_name) == 1:
                    obsolete_nodes.append(node_name)
                    down_edge = down_edges[node_name]
                    obsolete_edges.append(down_edge)
                    for up_edge in up_edges[node_name]:
                        obsolete_edges.append(up_edge)
                        new_edges.append([up_edge[0], down_edge[1]])
                    mission_complete = False
                    break

        m['nodes'] = [node for node in m['nodes'] if node['name'] not in obsolete_nodes]
        m['edges'] = [edge for edge in m['edges'] if edge not in obsolete_edges] + new_edges
        edges_set = []
        for edge in m['edges']:
            if edge not in edges_set:
                edges_set.append(edge)
        m['edges'] = edges_set

    for gauge in obsolete_gauges:
        for p in list(m['parameters']):
            parts = p.split('/')
            if gauge in parts:
                m['parameters'].pop(p, None)

        for r in list(m['recorders']):
            name_parts = r.split('/')
            node_parts = m['recorders'][r].get('node', '').split('/')
            parameter_parts = m['recorders'][r].get('parameter', '').split('/')
            if gauge in name_parts + node_parts + parameter_parts:
                m['recorders'].pop(r, None)

    return m


def prepare_planning_model(m, outpath, steps=12, debug=False):

    # update time step
    # m['timestepper']['end'] = m['timestepper']['start']
    # m['timestepper']['timestep'] = 'M'
    # m['metadata']['title'] += ' - planning'

    m = simplify_network(m, delete_gauges=True)

    all_steps = range(steps)

    new_nodes = []
    new_edges = []
    new_parameters = {}
    new_recorders = {}

    gauges = {}

    parameters_to_expand = []
    parameters_to_delete = []
    black_list = ['min_volume', 'max_volume']
    storage_recorders = {}

    for node in m['nodes']:
        old_name = node['name']
        node_type = node['type']

        for key, value in node.items():
            if key in black_list:
                continue
            if node_type == 'Storage' and key == 'cost':
                continue
            if type(value) == str and value in m['parameters']:
                if value not in parameters_to_expand:
                    parameters_to_expand.append(value)

        res_class = 'network'
        # res_name = 'network'
        # name_parts = old_name.replace(' [', '/').replace(']', '').split('/')
        # if len(name_parts) > 1 and name_parts[1] in ['node', 'link']:
        #     res_name, res_class = name_parts
        res_name = old_name
        metadata = json.loads(node.get('comment', '{}'))
        res_class = metadata.get('resource_class', 'network')

        for step in all_steps:
            t = step + 1
            new_node = node.copy()
            new_res_name = '{}/{}'.format(old_name, t)
            next_res_name = '{}/{}'.format(old_name, t + 1)
            new_node['name'] = new_res_name

            month = '/{}'.format(t)

            if node_type == 'Storage' and node.get('max_volume'):
                # 1. rename and empty storage for original storage node
                for key in ['cost', 'min_volume', 'max_volume', 'initial_volume']:
                    new_node.pop(key, None)
                    new_node['max_volume'] = 0.0
                    new_node['initial_volume'] = 0.0
                new_nodes.append(new_node)

                # 2. add a catchment to represent initial storage
                if step == 0:
                    input_name = old_name + ' [input]'
                    storage_input = {
                        'name': input_name,
                        'type': 'Catchment',
                        'flow': node.get('initial_volume', 0.0)
                    }
                    new_nodes.append(storage_input)
                    # 2.1 connect inflow to new "reservoir"
                    new_edges.append([input_name, new_res_name])

                # 3. create new storage node as link
                link_reservoir_base_name = old_name + ' [link]'
                link_reservoir_name = link_reservoir_base_name + '/{}'.format(t)
                storage_link = {
                    'name': link_reservoir_name,
                    'type': 'Link',
                }
                if 'min_volume' in node:
                    storage_link['min_flow'] = node['min_volume']
                if 'max_volume' in node:
                    storage_link['max_flow'] = node['max_volume']
                # if 'cost' in node:
                #     storage_link['cost'] = node['cost']
                # for now, set cost to zero (by omission)
                new_nodes.append(storage_link)

                # 3.1 connect this reservoir to new link reservoir
                new_edges.append([new_res_name, link_reservoir_name])

                # 3.2 connect new link reservoir to next reservoir
                if step != all_steps[-1]:
                    new_edges.append([link_reservoir_name, next_res_name])

                # 3.3 note we need to update storage recorders
                storage_recorders[node['name']] = link_reservoir_base_name

                # 4. create outflow node for reservoir
                if step == all_steps[-1]:
                    output_name = old_name + ' [output]'
                    storage_output = {
                        'name': output_name,
                        'type': 'Output'
                    }
                    new_nodes.append(storage_output)
                    # 4.1 connect outflow to new "reservoir"
                    new_edges.append([link_reservoir_name, output_name])

            else:
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
                                if len(parts) == 2:
                                    new_values.append(v + month)
                                elif len(parts) == 3:
                                    attr = parts[-2]
                                    block = parts[-1]
                                    new_v = '{}/{}/{}/{}'.format(res_name, attr, t, block)
                                    new_values.append(new_v)
                                else:
                                    new_values.append(v)
                            else:
                                new_values.append(v)
                        new_node[key] = new_values

                new_nodes.append(new_node)

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

        if param_name in parameters_to_delete:
            continue

        # Delete storage value (at least for now)
        if '/Storage Value' in param_name:
            continue

        parts = param_name.split('/')
        param = m['parameters'][param_name]
        res_name = None
        attribute = None
        block = None
        if len(parts) == 2:
            res_name, attribute = parts
        elif len(parts) == 3:
            res_name, attribute, block = parts
            block = int(block)

        if attribute in ['Observed Flow', 'Observed Storage']:
            continue

        if param_name in parameters_to_expand or 'node' in param:
            for step in all_steps:
                t = step + 1
                new_param_name = '{}/{}/{}'.format(res_name, attribute, t)
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
            if recorder['node'] in storage_recorders:
                recorder['type'] = 'NumpyArrayNodeRecorder'
                recorder['node'] = storage_recorders[recorder['node']]
            elif '/storage' in recorder_name:
                continue  # old storage nodes will be zero storage
            if not debug:
                recorder['node'] += '/1'  # record just the first time step results
                new_recorders[recorder_name] = recorder
            else:
                for step in all_steps:
                    t = step + 1
                    new_recorder = recorder.copy()
                    new_recorder['node'] += '/{}'.format(t)
                    new_recorders['{}/{}'.format(recorder_name, t)] = new_recorder

    # update the model
    m['nodes'] = new_nodes
    m['edges'] = new_edges
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    with open(outpath, 'w') as f:
        json.dump(m, f, indent=4)
    return


def run_model(basin, network_key, debug=False):
    # ========================
    # Set up model environment
    # ========================

    root_dir = os.path.join(os.getcwd(), basin)
    bucket = 'openagua-networks'
    model_path = os.path.join(root_dir, 'pywr_model_cleaned.json')

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

    # prepare paths
    root, filename = os.path.split(model_path)
    base, ext = os.path.splitext(filename)

    # simplify model
    simplified_filename = 'pywr_model_simplified.json'.format(base)
    simplified_model_path = os.path.join(root, simplified_filename)

    # prepare the model files
    with open(model_path, 'r') as f:
        m = json.load(f)

    m = simplify_network(m, delete_gauges=True)
    # with open(simplified_model_path, 'w') as f:
    #     json.dump(f, m, indent=4)
    with open(simplified_model_path, 'w') as f:
        f.write(json.dumps(m, indent=4))

    # Area for testing monthly model
    include_monthly = True

    if include_monthly:

        # create filenames, etc.
        monthly_filename = 'pywr_model_monthly.json'.format(base)
        monthly_model_path = os.path.join(root, monthly_filename)

        prepare_planning_model(m, monthly_model_path, debug=debug == 'm')

        # create pywr model
        monthly_model = Model.load(monthly_model_path, path=monthly_model_path)
        # monthly_model = Model.load(monthly_model_path, path=monthly_model_path, solver='glpk-edge')

        # set model mode to planning
        setattr(monthly_model, 'mode', 'planning')

        # set time steps
        monthly_model.timestepper.end -= relativedelta(months=12)
        start = monthly_model.timestepper.start
        end = monthly_model.timestepper.end

        # setup the planning model
        now = datetime.now()
        monthly_model.setup()
        print('Model setup in {} seconds'.format((datetime.now()-now).seconds))

        if debug == 'm':

            dates = pd.date_range(start=start, end=end, freq='MS')  # MS = month start

            nodes_of_type = {}
            # for node in monthly_model.nodes:
            #     nodes_of_type[node.type] = node.name
            fn_tpl = 'monthly_{v}_S{level}.csv'

            for date in tqdm(dates, ncols=80, disable=False):
                # print(date)
                monthly_model.timestepper.start = date
                # monthly_model.timestepper.end = date
                monthly_model.step()
                if date == dates[0]:
                    monthly_dir = './results'
                    # xl_path = os.path.join(monthly_dir, 'monthly_results.xlsx')
                    # with ExcelWriter(xl_path) as xlwriter:
                    df = monthly_model.to_dataframe()
                    df.columns = df.columns.droplevel(1)
                    variables = set([c.split('/')[2] for c in df.columns])
                    for v in variables:
                        node_names = []
                        month_numbers = []
                        col_names = []
                        for c in df.columns:
                            res_class, res_name, variable, month_str = c.split('/')
                            if variable == v:
                                col_names.append(c)
                                node_names.append(res_name)
                                month_numbers.append(int(month_str))
                        df_filtered = df[col_names]
                        df_filtered.columns = pd.MultiIndex.from_arrays([node_names, month_numbers])
                        df0 = df_filtered.stack(level=0)
                        # df1 = df_filtered.stack(level=1)
                        path0 = os.path.join(monthly_dir, fn_tpl.format(v=v, level=0))
                        # path1 = os.path.join(monthly_dir, fn_tpl.format(v=v, level=1))
                        df0.index.names = ['Start month', 'Resource']
                        df0.to_csv(path0)
                        # df1.index.names = ['Start month', 'Planning month']
                        # df1.to_csv(path1)

                        # df0.to_excel(xlwriter, sheet_name=v)

            print('...done')
            return

    # ==================
    # Create daily model
    # ==================
    # daily_model = Model.load(model_path, path=model_path)
    daily_model = Model.load(simplified_model_path, path=simplified_model_path)
    daily_model.setup()

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
parser.add_argument("-d", "--debug", help="Debug ('m' or 'd')")
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')
debug = args.debug

run_model(basin, network_key, debug)

print('done!')
