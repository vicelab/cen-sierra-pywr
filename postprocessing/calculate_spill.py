import os
import glob
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

flood_controls = {
    'tuolumne': 'Don Pedro Lake Flood Control',
    'merced': 'Exchequer Dam Flood Release',
    'upper_san_joaquin': 'Millerton Lake Flood Release'
}

ifrs = {
    # 'stanislaus': 'IFR bl Goodwin Reservoir',
    'tuolumne': 'IFR at La Grange',
    'merced': 'IFR at Shaffer Bridge',
    'upper_san_joaquin': 'IFR bl Millerton Lake',
}


def calculate_uncontrolled_spill(dataset_dir):
    p = Path(dataset_path)
    basin = [part for part in p.parts if part in ifrs]

    if not basin:
        return
    else:
        basin = basin[0]

    flood_control = flood_controls[basin]
    ifr = ifrs[basin]

    filepath = os.path.join(dataset_dir, 'InstreamFlowRequirement_Flow_mcm.csv')
    _df = pd.read_csv(filepath, index_col=0, parse_dates=False)
    n_scenarios = list(_df.index).index('Date')
    header = list(range(n_scenarios+1))

    def read_csv(filename, loc):
        filepath = os.path.join(dataset_dir, filename)
        df = pd.read_csv(filepath, index_col=0, parse_dates=True, header=header)
        df = df.xs(loc, axis=1, level=0, drop_level=False)
        df.rename(columns={loc: flood_control}, inplace=True)
        return df

    flood_reqt_df = read_csv('PiecewiseLink_Requirement_mcm.csv', flood_control)
    ifr_flow_df = read_csv('InstreamFlowRequirement_Flow_mcm.csv', ifr)
    ifr_reqt_df = read_csv('InstreamFlowRequirement_Min Flow_mcm.csv', ifr)

    df = ifr_flow_df - ifr_reqt_df - flood_reqt_df
    df[df < 1e-3] = 0
    df.plot(figsize=(12, 7))
    plt.show()

    filepath = os.path.join(dataset_dir, 'UncontrolledRelease_Flow_mcm.csv')
    df.to_csv(filepath)


# set up paths
root_dir = '.\\results'
run_name = 'All IFR scenarios - 2021-08-29'
# run_name = 'All IFR scenarios'
run_dir = os.path.join(root_dir, run_name)

dataset_paths = []
for path in os.walk(run_dir):
    if len(path[-1]):
        dataset_paths.append(path[0])

# process data
for dataset_path in dataset_paths:
    print('Processing {}'.format(dataset_path))
    try:
        calculate_uncontrolled_spill(dataset_path)
    except:
        print('oops!')
    # break
