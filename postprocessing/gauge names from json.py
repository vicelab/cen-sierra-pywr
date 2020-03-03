import json
import csv

basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

gauges_list = []
for basin in basins:
    m = json.load(open('../{}/pywr_model.json'.format(basin)))
    up_nodes = {}
    down_nodes = {}
    nodes = {n['name']: n for n in m['nodes']}
    for n1, n2 in m['edges']:
        up_nodes[n2] = up_nodes.get(n2, []) + [n1]
        down_nodes[n1] = down_nodes.get(n1, []) + [n2]

    included = []
    for node in m['nodes']:
        node_gauge_name = node.get('gauge')
        if node_gauge_name:
            gauges_list.append([node['name'], node_gauge_name])
            included.append(node['name'])

    for node in m['nodes']:

        node_gauge_name = node.get('gauge')
        if node['type'] != 'RiverGauge':
            continue
        gauge_name = node['name']
        up_node = nodes[up_nodes[gauge_name][0]]
        metadata = json.loads(up_node.get('comment', '{}'))
        gauged_node = up_nodes[up_node['name']][0] if metadata.get('resource_class') == 'link' else up_node['name']
        if gauged_node in included:
            # maybe it's a reservoir, so we should look down instead
            down_node = nodes[down_nodes[gauge_name][0]]
            metadata = json.loads(down_node.get('comment', '{}'))
            gauged_node = down_nodes[down_node['name']][0] if metadata.get('resource_class') == 'link' else down_node['name']
            if gauged_node in included:
                continue
        included.append(gauged_node)
        gauges_list.append([gauged_node, gauge_name])

with open('../dashapp/gauges.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(gauges_list)

print('done!')
