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
        gauged_node = up_nodes[up_nodes[gauge_name][0]][0]
        if gauged_node in included:
            # maybe it's a reservoir, so we should look down instead
            gauged_node = down_nodes[down_nodes[gauge_name][0]][0]
            if gauged_node in included:
                continue
        included.append(gauged_node)
        gauges_list.append([gauged_node, gauge_name])

with open('../dashapp/gauges.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(gauges_list)

print('done!')
