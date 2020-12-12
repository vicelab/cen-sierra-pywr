import json
from sierra.utilities import simplify_network

RIM_DAMS = {
    'stanislaus': 'New Melones Lake',
}

PARAMETERS_TO_EXPAND = {
    'stanislaus': [
        'New Melones Apr-Jul Runoff',
        # 'New Melones Lake/Water Year Type',
        'New Melones Lake/Storage Demand'
    ],
    'common': [
        'San Joaquin Valley WYT',
        'San Joaquin Valley WYI'
    ]
}

PARAMETERS_TO_REMOVE = {
    'stanislaus': [
        'New Melones Lake/Water Year Type'
    ]
}


def prepare_planning_model(m, basin, climate, outpath, steps=12, blocks=8, parameters_to_expand=None, debug=False,
                           remove_rim_dams=False):
    """
    Convert the daily scheduling model to a planning model.
    :param m:
    :param outpath:
    :param steps:
    :param blocks:
    :param parameters_to_expand:
    :param debug:
    :param include_rim_dams: Not used.
    :return:
    """
    # update time step
    # m['timestepper']['end'] = m['timestepper']['start']
    # m['timestepper']['timestep'] = 'M'
    # m['metadata']['title'] += ' - planning'

    parameters_to_expand = PARAMETERS_TO_EXPAND.get(basin, []) + PARAMETERS_TO_EXPAND.get('common', [])

    m = simplify_network(m, basin=basin, climate=climate, delete_gauges=True, delete_observed=True,
                         delete_scenarios=False)

    num_scenarios = 1
    for scenario in m.get('scenarios', []):
        num_scenarios *= scenario['size']

    all_steps = range(steps)

    new_nodes = []
    new_edges = []
    new_parameters = {}
    new_recorders = {}

    updated_node_names = {}

    gauges = {}

    parameters_to_expand = parameters_to_expand or []
    parameters_to_delete = []
    # black_list = ['min_volume', 'max_volume']
    black_list = ['max_volume']
    storage_recorders = {}

    if remove_rim_dams:
        rim_dam = RIM_DAMS.get(basin)
        parameters_to_remove = PARAMETERS_TO_REMOVE.get(basin, [])
        downstream_nodes = []
        downstream_edges = []
        finished = False
        while not finished:
            finished = True
            for n1, n2 in m['edges']:
                if (n1 == rim_dam or n1 in downstream_nodes) and n2 not in downstream_nodes:
                    downstream_nodes.append(n2)
                    finished = False
        m['nodes'] = [n for n in m['nodes'] if n['name'] not in downstream_nodes]
        m['edges'] = [e for e in m['edges'] if e[1] not in downstream_nodes and e[0]]
        for section in ['parameters', 'recorders']:
            keys = list(m[section].keys())
            for key in keys:
                parts = key.split('/')
                if len(parts) > 1 and parts[0] in downstream_nodes:
                    del m[section][key]

                if section == 'parameters' and key in parameters_to_remove:
                    del m[section][key]

        for i, n in enumerate(m['nodes']):
            if n['name'] == rim_dam:
                m['nodes'][i] = {
                    'name': rim_dam,
                    'type': 'Output',
                    'cost': 1
                }
                break

    for node in m['nodes']:
        old_name = node['name']
        node_type = node['type']

        # delete gauge
        node.pop('gauge', None)

        for key, value in node.items():
            if key in black_list:
                continue
            if node_type == 'Reservoir' and key == 'cost':
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

            if node_type == 'Reservoir' and node.get('max_volume'):
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
                        'flow': {
                            "type": "Planning_Initial_Storage",
                            "reservoir": old_name
                        }
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
                cost = node.get('cost', None)
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
                virtual_storage.pop('level', None)
                virtual_storage.pop('cost', None)
                # level = virtual_storage.get('level')
                # if type(level) == str:
                #     if level not in parameters_to_expand:
                #         parameters_to_expand.append(level)
                #     virtual_storage['level'] += '/{}'.format(t)
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
                        if key in ["max_flow", "turbine_capacity"]:
                            # TODO: convert capacities to formulas w/ day-month conversion
                            new_node[key] *= 30

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

        if attribute in ['Observed Flow', 'Observed Storage', 'Elevation']:
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
                    new_param['url'] = new_param['url'].replace('/runoff_aggregated/', '/runoff_monthly_forecasts/')
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
                    for control_curve in param['control_curves']:
                        if isinstance(control_curve, str):
                            new_param['control_curves'].append(control_curve + month_suffix)
                        else:
                            new_param['control_curves'].append(control_curve)

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
    for table_name, table in m.get('tables', {}).items():
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

                # flow
                recorder_name = node_name.replace('/', '/{}/'.format('flow'))
                new_recorders[recorder_name] = {
                    'type': 'NumpyArrayNodeRecorder',
                    'node': node_name,
                    # 'comment': node_type
                }

                # cost
                # for block in range(blocks):
                #     recorder_name = node_name.replace('/', '/{}/{}/'.format('cost', block+1))
                #     parameter_name = recorder_name.replace('cost', 'Cost')
                #     if parameter_name in new_parameters:
                #         new_recorders[recorder_name] = {
                #             'type': 'NumpyArrayParameterRecorder',
                #             'parameter': parameter_name,
                #             # 'comment': node_type
                #         }
                #     else:
                #         continue

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

    # # Fix a Pywr bug that prevents loading a control curve parameter defined by a virtual reservoir
    # virtual_storages = [n['name'] for n in new_nodes if n['type'].lower() == 'virtualstorage']
    # parameters_to_move = {}
    # for param_name, param in new_parameters.items():
    #     if param.get('storage_node') in virtual_storages:
    #         parameters_to_move[param_name] = param
    #
    # # embed param directly in node
    # for node in new_nodes:
    #     for k, v in node.items():
    #         if isinstance(v, str) and v in parameters_to_move:
    #             node[k] = parameters_to_move[v]
    #         elif isinstance(v, list):
    #             for j, item in enumerate(v):
    #                 if item in parameters_to_move:
    #                     node[k][j] = parameters_to_move[item]
    #
    # # embed param directly in param
    # for param_name, param in new_parameters.items():
    #     for k, v in param.items():
    #         if isinstance(v, str) and v in parameters_to_move:
    #             new_parameters[param_name][k] = parameters_to_move[v]
    #         elif isinstance(v, list):
    #             for j, item in enumerate(v):
    #                 if item in parameters_to_move:
    #                     new_parameters[param_name][k][j] = parameters_to_move[item]
    #
    # for param_name in parameters_to_move:
    #     del new_parameters[param_name]
    #
    # del parameters_to_move
    # # ...end fix bug

    # update the model
    m['nodes'] = new_nodes
    m['edges'] = new_edges
    m['tables'] = new_tables
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    with open(outpath, 'w') as f:
        json.dump(m, f, indent=4)
    return
