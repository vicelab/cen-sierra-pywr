from os import environ, path
from shutil import copytree
from distutils.dir_util import copy_tree
from itertools import product
from sierra.run_basin_model import run_model

nblocks = [2, 3, 4, 5, 6, 7, 8, 9, 10]
# nblocks = [8]
months = [8]

data_path = environ['SIERRA_DATA_PATH']

start_year = 2000
end_year = 2010
kwargs = dict(
    start='{}-10-01'.format(start_year),
    end='{}-09-30'.format(end_year),
    data_path=data_path,
    show_progress=False,
    study_name='Blocks sensitivity analysis'
)
for nb, m in list(product(nblocks, months)):
    # 1. set up price data

    src_monthly = '../../higrid-piecewise-linearization/results/method=fitfast step=monthly blocks={}'.format(nb)
    dst_monthly = path.join(data_path, 'common/energy prices')
    copy_tree(src_monthly, dst_monthly, update=True)

    # 2. run model
    kwargs.update(
        include_planning=m > 0,
        run_name='blocks={}'.format(nb),
        n_blocks=nb,
        planning_months=m
    )
    run_model('historical/Livneh', 'stanislaus', **kwargs)
