import json

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

    updated_node_names = {}

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
                # if 'min_volume' in node:
                #     storage_link['min_flow'] = node['min_volume']
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
            new_n1 = '{}/{}'.format(n1, t)
            new_n2 = '{}/{}'.format(n2, t)
            new_edges.append([
                updated_node_names.get(new_n1, new_n1),
                updated_node_names.get(new_n2, new_n2),
            ])

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
                    new_param['url'] = new_param['url'].replace('/runoff/', '/runoff_monthly_forecasts/')
                    new_param['column'] = '{:02}'.format(t)
                    # new_param['parse_dates'] = False
                if 'node' in param:
                    new_param['node'] += '/{}'.format(t)
                if 'storage_node' in param:
                    new_param['storage_node'] += '/{}'.format(t)

                new_parameters[new_param_name] = new_param
            continue

        new_parameters[param_name] = param

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
    m['parameters'] = new_parameters
    m['recorders'] = new_recorders

    with open(outpath, 'w') as f:
        json.dump(m, f, indent=4)
    return
