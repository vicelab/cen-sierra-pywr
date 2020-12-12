import os
import pandas as pd
from loguru import logger


def check_nan(basin_path, climate):
    def _check_nan(path, total_nan=0):
        if os.path.isdir(path):
            for subpath in os.listdir(path):
                fullsubpath = os.path.join(path, subpath)
                total_nan = _check_nan(fullsubpath, total_nan)

        else:
            ext = os.path.splitext(path)[-1]
            if ext == '.csv':
                df = pd.read_csv(path)

            else:
                return total_nan

            count_nan = df.isnull().sum().sum()

            try:
                assert (count_nan == 0)
            except:
                logger.warning('NaN found in {}'.format(path))

            total_nan += count_nan

        return total_nan

    for toppath in os.listdir(basin_path):

        total_nan = 0

        if toppath == 'gauges':
            continue

        if toppath == 'hydrology':
            climate_path = os.path.join(basin_path, toppath, climate)
            total_nan += _check_nan(climate_path, total_nan)
        else:
            fulltoppath = os.path.join(basin_path, toppath)
            total_nan += _check_nan(fulltoppath, total_nan)

    return total_nan
