import os
import pandas as pd

FRACTIONS = dict(a=0.42, b=0.03, c=0.47, d=0.08)


def disaggregate_SJN_09_subwatershed(scenario_path):
    """
    This scripts disaggregates the original SJN_09 subwatersheds into four smaller subcatchments.
    :param scenarios_path:
    :param scenarios:
    :return:
    """

    hydrology_path = os.path.join(scenario_path, 'runoff')

    sjn09_path = os.path.join(hydrology_path, 'tot_runoff_sb09_mcm.csv')
    df = pd.read_csv(sjn09_path, index_col=0, header=0, parse_dates=True)

    for subsubwat in ['a', 'b', 'c', 'd']:
        df2 = df * FRACTIONS[subsubwat]
        df2.to_csv(sjn09_path.replace('09', '09{}'.format(subsubwat)))