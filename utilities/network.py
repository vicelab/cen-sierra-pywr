import os
import json


def simplify_network(m, scenario_path=None, basin=None, climate=None, delete_gauges=False, delete_observed=True, delete_scenarios=False,
                     aggregate_runoff=True, create_graphs=False):
    # simplify the network
    mission_complete = False
    obsolete_gauges = []

    if delete_scenarios:
        # scenarios = []
        # for scen in m.get('scenarios', []):
        #     if scen['name'] == 'Price Year':
        #         scenarios.append(scen)
        #     else:
        #         scen['size'] = 1
        #         scenarios.append(scen)
        # m['scenarios'] = scenarios
        m.pop('scenarios', None)
    obsolete_nodes = []

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
            down_edges[a] = [edge] if a not in down_edges else down_edges[a] + [edge]
            up_edges[b] = [edge] if b not in up_edges else up_edges[b] + [edge]

        obsolete_edges = []
        new_edges = []

        node_lookup = {n['name']: n for n in m['nodes']}

        for node in m['nodes']:
            # is the node a simple link? if so, we might be able to remove it
            node_name = node['name']
            node_type = node['type'].lower()
            metadata = json.loads(node.get('comment', '{}'))
            keys_set = set(node.keys())

            # delete links adjacent to hydropower facilities
            if len({'cost', 'max_flow'} & keys_set) >= 1 and up_nodes.count(
                    node_name) == 1 \
                    and down_nodes.count(node_name) == 1 \
                    and 'hydropower' not in node_type \
                    and 'reservoir' not in node_type:
                up_edge = up_edges[node_name][0]
                up_node = node_lookup[up_edge[0]]
                up_type = up_node['type'].lower()
                down_edge = down_edges[node_name][0]
                down_node = node_lookup[down_edge[1]]
                down_type = down_node['type'].lower()
                # print(node_name, down_type)
                if 'hydropower' in up_type or 'hydropower' in down_type:
                    obsolete_nodes.append(node_name)
                    obsolete_edges.extend([up_edge, down_edge])
                    new_edges.append([up_node['name'], down_node['name']])
                    mission_complete = False
                    break

            if keys_set in [{'name', 'type'}, {'name', 'type', 'comment'}] and not metadata.get('keep') \
                    or delete_gauges and node_type == 'rivergauge' \
                    or node_type == 'reservoir' and not node.get('max_volume'):
                if delete_gauges and node_type == 'rivergauge':
                    obsolete_gauges.append(node_name)
                if down_nodes.count(node_name) == 0:
                    # upstream-most node
                    down_edge = down_edges[node_name][0]
                    obsolete_nodes.append(node_name)
                    obsolete_edges.append(down_edge)
                    mission_complete = False
                    break
                elif up_nodes.count(node_name) == 1:
                    down_edge = down_edges[node_name][0]
                    obsolete_nodes.append(node_name)
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

    # delete obsolete parameters and recorders
    obsolete_gauges_set = set(obsolete_gauges)
    obsolete_nodes_set = set(obsolete_nodes)
    for p in list(m['parameters']):
        parts = p.split('/')
        if parts[0] in obsolete_gauges:
            m['parameters'].pop(p, None)
        elif delete_observed and '/observed' in p.lower():
            m['parameters'].pop(p, None)
        elif parts[0] in obsolete_nodes:
            m['parameters'].pop(p, None)

    for r in list(m['recorders']):
        name_parts = r.split('/')[0:1]
        node_parts = m['recorders'][r].get('node', '').split('/')
        parameter_parts = m['recorders'][r].get('parameter', '').split('/')
        names_set = set(name_parts + node_parts + parameter_parts)
        if names_set & obsolete_gauges_set or names_set & obsolete_nodes_set:
            m['recorders'].pop(r, None)
        elif delete_observed and '/observed' in r:
            m['recorders'].pop(r, None)

    if aggregate_runoff:
        subwat_groups = {}
        obsolete_subwats = []
        new_subwats = []
        new_nodes = []
        new_edges = []
        for n1, n2 in m['edges']:
            if ' Headflow' in n1:
                obsolete_subwats.append(n1)
                new_subwat = '{} Inflow'.format(n2)
                if new_subwat not in new_subwats:
                    new_subwats.append(new_subwat)
                    new_node = node_lookup[n1].copy()
                    new_node.update(
                        name=new_subwat,
                        flow='{}/Runoff'.format(new_subwat)
                    )
                    new_nodes.append(new_node)
                    new_edges.append([new_subwat, n2])
            else:
                new_edges.append([n1, n2])

        m['nodes'] = new_nodes + [n for n in m['nodes'] if n['name'] not in obsolete_subwats]
        m['edges'] = new_edges

        for subwat in obsolete_subwats:
            flow_param = node_lookup[subwat]['flow']
            del m['parameters'][flow_param]
        recorder_names = list(m['recorders'])
        for r in recorder_names:
            recorder = m['recorders'][r]
            node = recorder.get('node')
            if node and node in obsolete_subwats:
                del m['recorders'][r]

        for node in new_nodes:
            param_name = node['flow']
            if scenario_path:
                url = "{scenario_path}/runoff_aggregated/{param} mcm.csv".format(
                    datapath=os.environ.get('SIERRA_DATA_PATH'),
                    basin=basin.replace('_', ' ').title(),
                    climate=climate,
                    param=param_name.split('/')[0]
                )
            else:
                url = "{datapath}/{basin} River/hydrology/{climate}/runoff_aggregated/{param} mcm.csv".format(
                    datapath=os.environ.get('SIERRA_DATA_PATH'),
                    basin=basin.replace('_', ' ').title(),
                    climate=climate,
                    param=param_name.split('/')[0]
                )
            new_param = {
                "type": "InflowDataframe",
                "url": url,
                "column": "flow",
                "index_col": 0,
                "parse_dates": True
            }
            m['parameters'][param_name] = new_param

    return m
