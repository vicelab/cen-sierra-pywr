import os
import json

from loguru import logger

fillcolors = {
    'reservoir': 'blue',
    'virtualstorage': 'blue',
    'hydropower': 'red',
    'piecewisehydropower': 'red',
    'instreamflowrequirement': 'green',
    'piecewiseinstreamflowrequirement': 'green',
    'catchment': 'lightblue',
    'output': 'black',
    'breaklink': 'lightgrey'
}

fontcolors = {
    'reservoir': 'white',
    'virtualstorage': 'white',
    'hydropower': 'white',
    'piecewisehydropower': 'white',
    'instreamflowrequirement': 'black',
    'output': 'white'
}


# dot = Digraph(comment='System')

def create_schematic(basin, version, format='pdf', render=False, view=False):
    try:
        from graphviz import Digraph, ExecutableNotFound
        from graphviz.backend import CalledProcessError
    except:
        logger.warning('Graphviz python package not installed.')
        return

    filename = 'pywr_model_Livneh'
    if version:
        filename += '_' + version
    filename += '.json'
    with open(os.path.join('models', basin, 'temp', filename)) as f:
        model = json.load(f)

    try:
        _dot = Digraph(name=basin, comment=basin, format=format)
    except ExecutableNotFound:
        logger.warning('Graphviz executable not found. Schematic not created.')

    for node in model['nodes']:

        node_name = node['name']
        if version == 'monthly':
            if ' [output]' in node_name:
                continue
            parts = node_name.split('/')
            if len(parts) > 1:
                base_node_name, month = parts
                if int(month) > 1 and not ('[original]' in node_name and int(month) == 2):
                    continue

        ntype = node['type'].lower()
        fillcolor = fillcolors.get(ntype, 'white')
        fontcolor = fontcolors.get(ntype, 'black')
        shape = 'rect' if ntype in ['reservoir', 'virtualstorage'] else 'oval'
        style = 'filled' if fillcolor else ''

        if ntype == 'virtualstorage':
            style += ',dashed'

        if version == 'monthly':
            shape = 'oval'
            if ntype == 'reservoir' or month == 2:
                fillcolor = fillcolors.get('breaklink')
                fontcolor = 'black'
        #             if '[link]' in node_name:
        #                 fillcolor = fillcolors.get('reservoir')
        #                 fontcolor = fontcolors.get('reservoir')

        _dot.node(node_name, shape=shape, style=style, fillcolor=fillcolor, fontcolor=fontcolor)

        if version == 'monthly' and ntype == 'virtualstorage':
            _dot.edge(node_name.replace('/', ' [link]/'), node_name, style='dashed')
    #         dot.node(node['name'], shape='shape', style=style, fillcolor=fillcolor, fontcolor=fontcolor)

    #     dot.edges(model['edges'])

    for edge in model['edges']:
        if version == 'monthly':
            n1, n2 = edge
            try:
                base_n1_name, m1 = n1.split('/')
                base_n2_name, m2 = n2.split('/')
                m1 = int(m1)
                m2 = int(m2)
                if (int(m1) > 1 or int(m2) > 1) and not (m1 == 1 and m2 == 2):
                    continue
            except:
                if '[output]' in n2:
                    continue
                else:
                    pass
        _dot.edges([edge])

    schematics_dir = './models/{}'.format(basin)
    gv_filename = 'graphviz_schematic{}.gv'.format('' if not version else '_' + version)
    if render:
        outpath = os.path.join(schematics_dir, gv_filename)
        try:
            _dot.render(outpath, view=view)
        except CalledProcessError as err:
            logger.warning('Could not create {} schematic. {}'.format(format, err))
    else:
        _dot.save(gv_filename, schematics_dir)


if __name__ == '__main__':
    # basins = ['stanislaus', 'merced', 'upper_san_joaquin', 'tuolumne']
    # basins = ['upper_san_joaquin']
    basin = 'stanislaus'
    # basins = ['merced']
    # version = None
    # version = 'cleaned'
    # version = 'simplified'
    version = 'monthly'

    create_schematic(basin, version, view=True)
