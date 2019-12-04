import os
import sys
import json
from itertools import product
from pywr.core import Model
from pywr.timestepper import Timestepper
from importlib import import_module
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
from common.tests import test_planning_model, get_planning_dataframe
import numpy as np
import pandas as pd

SECONDS_IN_DAY = 3600 * 24


class PlanningTimestepper(Timestepper):

    def setup(self):
        periods = self.datetime_index

        # Compute length of each period
        deltas = periods.to_timestamp(how='e') - periods.to_timestamp(how='s')
        # Round to nearest second
        deltas = np.round(deltas.total_seconds())
        # Convert to days
        deltas = deltas / SECONDS_IN_DAY
        self._periods = periods
        self._deltas = deltas
        self.reset()
        self._dirty = False


# PlanningTimestepper.register()


def simplify_network(m, delete_gauges=False, delete_observed=True):
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

            if delete_observed and '/observed' in p.lower():
                m['parameters'].pop(p, None)

        for r in list(m['recorders']):
            name_parts = r.split('/')
            node_parts = m['recorders'][r].get('node', '').split('/')
            parameter_parts = m['recorders'][r].get('parameter', '').split('/')
            if gauge in name_parts + node_parts + parameter_parts:
                m['recorders'].pop(r, None)

            if delete_observed and '/observed' in r:
                m['recorders'].pop(r, None)

    return m


def prepare_planning_model(m, outpath, steps=12, blocks=8, debug=False):
    """
    Convert the daily scheduling model to a planning model.
    :param m:
    :param outpath:
    :param steps:
    :param debug:
    :return:
    """
    # update time step
    # m['timestepper']['end'] = m['timestepper']['start']
    # m['timestepper']['timestep'] = 'M'
    # m['metadata']['title'] += ' - planning'

    m = simplify_network(m, delete_gauges=False, delete_observed=True)

    all_steps = range(steps)

    new_nodes = []
    new_edges = []
    new_parameters = {}
    new_recorders = {}

    updated_node_names = {}

    gauges = {}

    parameters_to_expand = [
        'New Melones Apr-Jul Runoff',
        'San Joaquin Valley WYT',
        'San Joaquin Valley WYI'
    ]
    parameters_to_delete = []
    # black_list = ['min_volume', 'max_volume']
    black_list = ['max_volume']
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
        metadata.update(type=node_type)
        node['comment'] = json.dumps(metadata)

        for step in all_steps:
            t = step + 1
            new_node = node.copy()
            new_res_name = '{}/{}'.format(old_name, t)
            new_node['name'] = new_res_name

            month = '/{}'.format(t)

            if node_type == 'Storage' and node.get('max_volume'):
                # 1. rename and empty storage for original storage node
                # for key in ['cost', 'min_volume', 'max_volume', 'initial_volume']:
                #     new_node.pop(key, None)
                #     new_node['max_volume'] = 0.0
                #     new_node['initial_volume'] = 0.0
                # new_nodes.append(new_node)
                original_reservoir_name = '{} [original]/{}'.format(old_name, t)
                next_reservoir_name = '{} [original]/{}'.format(old_name, t + 1)
                original_storage_node = {
                    'name': original_reservoir_name,
                    'type': 'BreakLink'
                }
                new_nodes.append(original_storage_node)
                updated_node_names[new_res_name] = original_reservoir_name

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
                    new_edges.append([input_name, original_reservoir_name])

                # 3. create new storage node as link
                link_reservoir_base_name = old_name + ' [link]'
                link_reservoir_name = link_reservoir_base_name + '/{}'.format(t)
                storage_link = {
                    'name': link_reservoir_name,
                    'type': 'Link',
                }
                # Actually, we don't want to do the following, since it might cause an infeasibility
                if 'min_volume' in node:
                    min_volume = node['min_volume']
                    if type(min_volume) == str:
                        if min_volume not in parameters_to_expand:
                            parameters_to_expand.append(min_volume)
                        min_volume += month
                    storage_link['min_flow'] = min_volume
                if 'max_volume' in node:
                    storage_link['max_flow'] = node['max_volume']
                cost = node.pop('cost', None)
                if cost:
                    if type(cost) == str:
                        if cost not in parameters_to_expand:
                            parameters_to_expand.append(cost)
                        cost += '/{}'.format(t)
                    storage_link['cost'] = cost
                # for now, set cost to zero (by omission)
                new_nodes.append(storage_link)

                # 3.1 connect this reservoir to new link reservoir
                new_edges.append([original_reservoir_name, link_reservoir_name])

                # 3.2 connect new link reservoir to next reservoir
                if step != all_steps[-1]:
                    new_edges.append([link_reservoir_name, next_reservoir_name])

                # 3.3 note we need to update storage recorders
                # storage_recorders[node['name']] = link_reservoir_base_name

                # 4. create virtual storage node to represent the original storage reservoir
                # the virtual storage node is not physically connected to the system,
                # but is nonetheless "filled" by flows in the system
                virtual_storage = node.copy()
                level = virtual_storage.get('level')
                if type(level) == str:
                    if level not in parameters_to_expand:
                        parameters_to_expand.append(level)
                    virtual_storage['level'] += '/{}'.format(t)
                virtual_storage.update({
                    'name': new_res_name,
                    'type': 'VirtualStorage',
                    'nodes': [link_reservoir_name],
                    'factors': [-1],
                    'initial_volume': 0.0,
                })
                virtual_storage.pop('min_volume', None)
                # virtual_storage.pop('cost', None)
                # if cost in m['parameters'] and cost not in parameters_to_delete:
                #     parameters_to_delete.append
                # for attr in ['cost', 'min_volume', 'max_volume', 'initial_volume']:
                #     val = virtual_storage.get(attr)
                #     if type(val) == str and val in m['parameters']:
                #         if val not in parameters_to_expand:
                #             parameters_to_expand.append(val)

                new_nodes.append(virtual_storage)

                # 5. create outflow node for reservoir
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
                            if value not in parameters_to_expand:
                                parameters_to_expand.append(value)

                    elif type(value) in [float, int]:
                        if "max_flow" in key:
                            new_node[key] *= 30  # TODO: figure out some scheme to get actual days

                    elif type(value) == list:
                        new_values = []
                        for j, v in enumerate(value):
                            if type(v) == str:
                                if v not in parameters_to_expand:
                                    parameters_to_expand.append(v)
                                parts = v.split('/')
                                if j == 0 or len(parts) == 2:
                                    for b in range(blocks):
                                        if len(parts) == 2:
                                            # no block-specific value, but still need to expand to number of blocks
                                            new_values.append(v + month)
                                            break
                                        elif len(parts) == 3:
                                            # there are block-specific parameters
                                            attr = parts[-2]
                                            # note the scheme: resource name / attribute / block / month
                                            new_v = '{}/{}/{}/{}'.format(res_name, attr, b + 1, t)
                                            new_values.append(new_v)
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
            new_n1 = '{}/{}'.format(n1, t)
            new_n2 = '{}/{}'.format(n2, t)
            new_edges.append([
                updated_node_names.get(new_n1, new_n1),
                updated_node_names.get(new_n2, new_n2),
            ])

    block_params_expanded = []

    for param_name, param in m['parameters'].items():
        if 'control_curves' in param:
            for cc in param['control_curves']:
                if type(cc) == str and cc not in parameters_to_expand:
                    parameters_to_expand.append(cc)

    for param_name in m['parameters']:

        if param_name in parameters_to_delete:
            continue

        # Delete storage value (at least for now)
        # if '/Storage Value' in param_name:
        #     continue

        parts = param_name.split('/')
        param = m['parameters'][param_name]
        res_name = None
        attribute = None
        block = None
        if len(parts) == 1:
            attribute = parts[0]
        elif len(parts) == 2:
            res_name, attribute = parts
        elif len(parts) == 3:
            res_name, attribute, block = parts
            block = int(block)

        if attribute in ['Observed Flow', 'Observed Storage']:
            continue

        if param_name in parameters_to_expand or 'node' in param:
            for step in all_steps:
                t = step + 1
                month_suffix = '/{}'.format(t)
                if block:
                    # check if we've already expanded this
                    block_param = (res_name, attribute, t)
                    if block_param in block_params_expanded:
                        continue  # continue if we have
                    block_params_expanded.append(block_param)

                new_param = param.copy()
                if attribute == 'Runoff':
                    new_param['url'] = new_param['url'].replace('/runoff/', '/runoff_monthly_forecasts/')
                    new_param['column'] = '{:02}'.format(t)
                    # new_param['parse_dates'] = False
                elif attribute == 'Turbine Capacity':
                    if new_param['type'] == 'constant':
                        # TODO: come up with a better method for converting PH capacity
                        # should be in custom class or table lookup
                        new_param['value'] *= 30
                if 'node' in param:
                    new_param['node'] += month_suffix
                if 'storage_node' in param:
                    new_param['storage_node'] += month_suffix
                if 'control_curves' in param:
                    new_param['control_curves'] = []
                    for cc in param['control_curves']:
                        new_param['control_curves'].append(cc + month_suffix)

                if block:
                    for b in range(blocks):
                        new_param_name = '/'.join([res_name, attribute, str(b + 1), str(t)])
                        new_parameters[new_param_name] = new_param
                else:
                    if res_name and attribute:
                        new_param_name = '/'.join([res_name, attribute, str(t)])
                    else:
                        new_param_name = '/'.join([attribute, str(t)])
                    new_parameters[new_param_name] = new_param
            continue

        new_parameters[param_name] = param

    new_tables = {}
    for table_name, table in m['tables'].items():
        if 'observed' in table_name.lower():
            continue
        if 'url' in table:
            table['url'] = table['url'].replace('daily', 'monthly')
        new_tables[table_name] = table

    if debug:
        for n in new_nodes:
            node_name = n['name']
            parts = node_name.split('/')
            month = int(parts[1]) if len(parts) > 1 else None
            node_type = n['type']
            if node_type == 'VirtualStorage':
                new_recorders[node_name.replace('/', '/{}/'.format('storage'))] = {
                    'type': 'NumpyArrayStorageRecorder',
                    'node': node_name,
                    # 'comment': node_type
                }
            elif 'hydropower' in node_type.lower():
                recorder_name = node_name.replace('/', '/{}/'.format('flow'))
                new_recorders[recorder_name] = {
                    'type': 'NumpyArrayNodeRecorder',
                    'node': node_name,
                    # 'comment': node_type
                }

    # for recorder_name in m['recorders']:
    #     recorder = m['recorders'][recorder_name]
    #     if 'node' in recorder:
    #         if recorder['node'] in gauges:
    #             continue
    #         if recorder['node'] in storage_recorders:
    #             recorder['type'] = 'NumpyArrayNodeRecorder'
    #             recorder['node'] = storage_recorders[recorder['node']]
    #         # elif '/storage' in recorder_name:
    #         #     continue  # old storage nodes will be zero storage
    #         if not debug:
    #             recorder['node'] += '/1'  # record just the first time step results
    #             new_recorders[recorder_name] = recorder
    #         else:
    #             for step in all_steps:
    #                 t = step + 1
    #                 new_recorder = recorder.copy()
    #                 new_recorder['node'] += '/{}'.format(t)
    #                 new_recorders['{}/{}'.format(recorder_name, t)] = new_recorder

    # update the model
    m['nodes'] = new_nodes
    m['edges'] = new_edges
    m['tables'] = new_tables
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    with open(outpath, 'w') as f:
        json.dump(m, f, indent=4)
    return


def run_model(basin, scenario, start, end, network_key, run_name="default", include_planning=False, simplify=True,
              debug=False, planning_months=12):
    months = planning_months

    # ========================
    # Set up model environment
    # ========================

    here = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.join(here, basin)
    os.chdir(here)

    climate_scenario, price_year = scenario

    bucket = 'openagua-networks'
    base_filename = 'pywr_model.json'
    model_filename_base = 'pywr_model_{}'.format(climate_scenario)
    model_filename = model_filename_base + '.json'

    base_path = os.path.join(root_dir, base_filename)
    model_path = os.path.join(root_dir, model_filename)

    # first order of business: update file paths in json file
    with open(base_path) as f:
        base_model = json.load(f)

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
                if climate_scenario != 'Livneh':
                    url = url.replace('Livneh', climate_scenario)
                if price_year != 2009:
                    url = url.replace('PY2009', 'PY{}'.format(price_year))
                param['url'] = url
            new_model_parts[model_part][pname] = param

    new_model_parts['parameters']['Price Year'] = {
        "type": "constant",
        "value": price_year
    }
    base_model.update(new_model_parts)
    base_model['timestepper']['start'] = start
    base_model['timestepper']['end'] = end
    with open(model_path, 'w') as f:
        json.dump(base_model, f, indent=4)

    # needed when loading JSON file
    # root_path = 's3://{}/{}/'.format(bucket, network_key)
    root_path = './data'
    os.environ['ROOT_S3_PATH'] = root_path

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
        # package = '.{}'.format(policy_folder)
        import_module(policy_module, policy_folder)

    # modules = [
    #     # ('IFRs', 'policies'),
    #     # ('domains', 'domains')
    # ]
    # # from domains import domains
    # for name, package in modules:
    #     try:
    #         import_module('{}.{}'.format(basin, name), package)
    #     except Exception as err:
    #         print(' [-] WARNING: {} could not be imported from {}'.format(name, package))
    #         print(type(err))
    #         print(err)

    modules = [
        # ('IFRs', 'policies'),
        # ('domains', 'domains')
    ]
    # from domains import domains

    # import domains
    import_module('.domains', 'domains')

    # import custom policies
    try:
        import_module('{}.policies'.format(basin))
    except Exception as err:
        print(' [-] WARNING: Could not import {} policies.'.format(basin))
        print(type(err))
        print(err)

    # prepare the model files
    if simplify or include_planning:
        with open(model_path, 'r') as f:
            m = json.load(f)

    if simplify:
        # simplify model
        simplified_filename = model_filename_base + '_simplified.json'
        simplified_model_path = os.path.join(root_dir, simplified_filename)

        m = simplify_network(m, delete_gauges=True, delete_observed=True)
        # with open(simplified_model_path, 'w') as f:
        #     json.dump(f, m, indent=4)
        with open(simplified_model_path, 'w') as f:
            f.write(json.dumps(m, indent=4))

        model_path = simplified_model_path

    # Area for testing monthly model
    save_results = True
    planning_model = None
    df_planning = None

    if include_planning:

        print('Creating planning model (this may take a minute or two)')

        # create filenames, etc.
        monthly_filename = model_filename_base + '_monthly.json'
        planning_model_path = os.path.join(root_dir, monthly_filename)

        prepare_planning_model(m, planning_model_path, steps=months, debug=save_results)

        # create pywr model
        planning_model = Model.load(planning_model_path, path=planning_model_path)

        # set model mode to planning
        setattr(planning_model, 'mode', 'planning')

        # set time steps
        start = planning_model.timestepper.start
        end = planning_model.timestepper.end
        end -= relativedelta(months=months)
        # planning_model.timestepper = PlanningTimestepper(start, end)

        planning_model.setup()

        if debug == 'm':
            test_planning_model(planning_model, months=months, save_results=save_results)
            return

    # ==================
    # Create daily model
    # ==================
    print('Loading daily model')
    from pywr.nodes import Storage
    m = Model.load(model_path, path=model_path)
    reservoirs = [n.name for n in m.nodes if type(n) == Storage and '(storage)' not in n.name]
    m.setup()

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    # IMPORTANT: The following can be embedded into the scheduling model via
    # the 'before' and 'after' functions.
    days_to_omit = 0
    if include_planning:
        end = m.timestepper.end
        new_end = end + relativedelta(months=-months)
        m.timestepper.end = new_end
    step = -1
    now = datetime.now()
    monthly_seconds = 0
    setattr(m, 'mode', 'scheduling')
    setattr(m, 'planning', planning_model if include_planning else None)

    for date in tqdm(m.timestepper.datetime_index, ncols=60, disable=False):
        step += 1
        try:

            # Step 1: run planning model & update daily model

            if include_planning and date.day == 1:
                # monthly_now = datetime.now()
                # Step 1a: update planning model
                # ...update start day
                # m.planning.timestepper.start = date.to_timestamp()
                m.planning.reset(start=date.to_timestamp())

                # ...update initial conditions (not needed for the first step)
                for res in reservoirs:
                    if step == 0:
                        initial_volume = m.nodes[res].initial_volume
                    else:
                        initial_volume = m.nodes[res].volume[-1]
                    m.planning.nodes[res + ' [input]'].min_flow = initial_volume
                    m.planning.nodes[res + ' [input]'].max_flow = initial_volume

                # Step 1b: run planning model
                m.planning.step()  # redundant with run, since only one timestep
                if debug == 'dm' and save_results:
                    df_month = get_planning_dataframe(m.planning)
                    if df_planning is None:
                        df_planning = df_month
                    else:
                        df_planning = pd.concat([df_planning, df_month])

                # Step 1c: update daily model with planning model results
                # print('Updating daily model')

                # this_monthly_seconds = (datetime.now() - monthly_now).total_seconds()
                # print('Monthly run in {} seconds'.format(this_monthly_seconds))
                # monthly_seconds += this_monthly_seconds

            # Step 3: run daily model
            m.step()
        except Exception as err:
            print('\nFailed at step {}'.format(date))
            print(err)
            raise
            # continue
            # break
    total_seconds = (datetime.now() - now).total_seconds()
    print('Total run: {} seconds'.format(total_seconds))
    print(
        'Monthly overhead: {} seconds ({:02}% of total)'.format(monthly_seconds, monthly_seconds / total_seconds * 100))

    # save results to CSV

    if df_planning is not None:
        df_planning.to_csv('./results/planning.csv')

    results = m.to_dataframe()
    results.index.name = 'Date'
    scenario_name = '{}_P{}'.format(climate_scenario, price_year)
    results_path = os.path.join('./results', basin, run_name, scenario_name)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    results.columns = results.columns.droplevel(1)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    results.to_csv(os.path.join(results_path, 'system_mcm.csv'))
    columns = {}
    nodes_of_type = {}
    for c in results.columns:
        res_name, attr = c.split('/')
        node = m.nodes[res_name]
        _type = type(node).__name__
        key = (_type, attr)
        if key in columns:
            columns[key].append(c)
        else:
            columns[key] = [c]
        nodes_of_type[_type] = nodes_of_type.get(_type, []) + [node]
    for (_type, attr), cols in columns.items():
        tab_path = os.path.join(results_path, '{}_{}_mcm'.format(_type, attr.title()))
        df = results[cols]
        df.columns = [c.split('/')[0] for c in cols]
        df.to_csv(tab_path + '.csv')

        if _type in ['Hydropower', 'PiecewiseHydropower'] and attr == 'flow':
            gen_df = df.copy()
            gen_path = os.path.join(results_path, '{}_Generation_MWh.csv'.format(_type))
            for c in df.columns:
                node = m.nodes[c]
                gen_df *= node.head * 0.9 * 9.81 * 1000 / 1e6
                gen_df.to_csv(gen_path)


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basin", help="Basin to run")
parser.add_argument("-nk", "--network_key", help="Network key")
parser.add_argument("-d", "--debug", help="Debug ('m' or 'd' or 'dm')")
parser.add_argument("-p", "--include_planning", help="Include planning model", action='store_true')
parser.add_argument("-n", "--run_name", help="Run name")
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')
debug = args.debug
include_planning = args.include_planning

# gcms = ['HadGEM2-ES', 'CNRM-CM5', 'CanESM2', 'MIROC5']
gcms = ['HadGEM2-ES', 'MIROC5']
rcps = ['85']
gcm_rcps = ['{}_rcp{}'.format(g, r) for g, r in product(gcms, rcps)]

if debug:
    planning_months = 8
    climate_scenarios = ['Livneh']
    price_years = [2009]
    # price_years = [2009]
else:
    planning_months = 12
    climate_scenarios = gcm_rcps
    price_years = [2030, 2060]

# climate_scenarios = gcm_rcps
# price_years = [2009]

scenarios = product(climate_scenarios, price_years)

for scenario in scenarios:
    climate, price_year = scenario
    if climate == 'Livneh':
        start_year = 2000
        if debug:
            end_year = 2003
        else:
            end_year = 2012
    else:
        start_year = 2030
        end_year = 2045
    start = '{}-10-01'.format(start_year)
    end = '{}-09-30'.format(end_year)
    run_model(
        basin, scenario, start, end, network_key,
        run_name=args.run_name,
        include_planning=include_planning,
        debug=debug,
        planning_months=planning_months
    )

print('done!')
