import json
import csv

basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

gauges_list = []
for basin in basins:
    m = json.load(open('../{}/pywr_model.json'.format(basin)))
    up_nodes = {}
    down_nodes = {}
    for n1, n2 in m['edges']:
        up_nodes[n2] = up_nodes.get(n2, []) + [n1]
        down_nodes[n1] = down_nodes.get(n1, []) + [n2]
    for node in m['nodes']:
        node_gauge_name = node.get('gauge')
        if node_gauge_name:
            gauges_list.append([node['name'], node_gauge_name])
            continue
        else:
            if node['type'] != 'RiverGauge':
                continue
            gauge_name = node['name']
            up_reach = up_nodes[gauge_name][0]
            gauged_node = up_nodes[up_reach][0]
            gauges_list.append([gauged_node, gauge_name])

with open('../dashapp/gauges.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(gauges_list)

print('done!')
