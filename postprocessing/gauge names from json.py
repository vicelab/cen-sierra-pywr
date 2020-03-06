import os
import json
import pandas as pd

basins = ['stanislaus', 'tuolumne', 'merced', 'upper_san_joaquin']

gauges_path = '../dashapp/gauges.csv'
gauges = {}
if os.path.exists(gauges_path):
    gauges_df = pd.read_csv(gauges_path, index_col=0, header=0, squeeze=True)
    gauges = gauges_df.to_dict()

for basin in basins:
    m = json.load(open('../{}/pywr_model.json'.format(basin)))
    up_nodes = {}
    down_nodes = {}
    nodes = {n['name']: n for n in m['nodes']}
    for n1, n2 in m['edges']:
        up_nodes[n2] = up_nodes.get(n2, []) + [n1]
        down_nodes[n1] = down_nodes.get(n1, []) + [n2]

    for node in m['nodes']:
        node_gauge_name = node.get('gauge')
        if node_gauge_name:
            gauges[node['name']] = node_gauge_name

    for node in m['nodes']:

        node_gauge_name = node.get('gauge')
        if node['type'] != 'RiverGauge':
            continue
        gauge_name = node['name']
        up_node = nodes[up_nodes[gauge_name][0]]
        metadata = json.loads(up_node.get('comment', '{}'))
        gauged_node = up_nodes[up_node['name']][0] if metadata.get('resource_class') == 'link' else up_node['name']

        # let's also check down node...
        down_node = nodes[down_nodes[gauge_name][0]]
        metadata = json.loads(down_node.get('comment', '{}'))
        if down_node['type'] == 'Output':
            gauged_node = down_nodes[down_node['name']][0] if metadata.get('resource_class') == 'link' else down_node['name']

        gauges[gauged_node] = gauge_name

df = pd.DataFrame.from_dict(gauges, orient='index', columns=['Gauge'])
df.index.name = 'Node'
df.to_csv(gauges_path)

print('done!')
