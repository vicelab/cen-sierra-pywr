from os import environ
from itertools import product
from sierra.run_basin_model import run_model

# nblocks = [2, 3, 4, 5, 6, 7, 8]
nblocks = [8]
months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

start_year = 2000
end_year = 2010
kwargs = dict(
    start='{}-10-01'.format(start_year),
    end='{}-09-30'.format(end_year),
    data_path=environ['SIERRA_DATA_PATH'],
    show_progress=False,
    study_name='Months sensitivity analysis'
)
for nb, m in list(product(nblocks, months)):
    # 1. set up price data

    # 2. run model
    kwargs.update(
        include_planning=m > 0,
        run_name='months={}'.format(m),
        n_blocks=nb,
        planning_months=m
    )
    run_model('historical/Livneh', 'stanislaus', **kwargs)
