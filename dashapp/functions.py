import os
import pandas as pd
from dashapp.constants import BASINS, PATH_TEMPLATES, ENSEMBLE_NAMES


def agg_by_resources(df, agg):
    levels = list(range(len(df.columns.levels)))
    # levels.pop(1)
    df = df.groupby(axis=1, level=0).agg(agg)
    # new_cols = [(c[0], agg) + tuple(c[1:]) for c in df.columns]
    new_cols = [(c, agg) for c in df.columns]
    df.columns = pd.MultiIndex.from_tuples(new_cols)
    return df


def get_resources(df, filterby=None):
    if not filterby:
        return []
    all_resources = sorted(set(df.columns.get_level_values(1)))
    return [r for r in all_resources if not filterby or r.replace(' ', '_') in filterby]
    # return all_resources


def consolidate_dataframe(df, resample):
    if not resample:
        fmt = '%j'
    else:
        fmt = '%m'
    _df = df.copy()
    _df.index = pd.MultiIndex.from_tuples([(date.strftime(fmt), str(date.year)) for date in df.index])
    _df = _df.unstack(level=-1)
    if not resample:
        dates = pd.date_range(start='2000-01-01', periods=len(_df.index), freq='D')
        _df.index = [d.strftime('%b-%d') for d in dates]
    else:
        dates = pd.date_range(start='2000-01-01', periods=len(_df.index), freq='MS')
        _df.index = [d.strftime('%b') for d in dates]
    return _df


def flow_to_energy(df_cfs, head):
    # df comes in as cfs...
    # MWh = Q[cms] * head[m] * eta * g[m/s^s] * rho[kg/m^3] * hours in day / 1e6
    df = df_cfs / 35.31 * head * 0.9 * 9.81 * 1000 * 24 / 1e6
    return df


def load_timeseries(results_path, basin, forcings, attr_id, basin_scenarios, nscenarios=1,
                    run='full run', tpl='mcm', multiplier=1.0, aggregate=None, filterby=None):
    full_basin = BASINS[basin].replace(' ', '_').lower()
    if run == 'development':
        data_dir = os.path.join(
            results_path,
            run,
            full_basin,
            forcings[0],
        )
        filename = attr_id.replace('-', '_') + '.csv'
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            return None

        header = list(range(len(basin_scenarios) + 1))

        df = pd.read_csv(filepath, index_col=0, parse_dates=True, header=header)

        start = 1
        end = start + len(df.columns.names[1:-1])
        levelvals = range(1, df.columns.nlevels)
        for i, val in enumerate(levelvals):
            if len(val) > 1:
                df.drop(val[1:], axis=1, level=1, inplace=True)
            df = df.droplevel(1, axis=1)
        new_levels = [(forcings[0], col) for col in df.columns]
        df.columns = pd.MultiIndex.from_tuples(new_levels)

    else:
        path = os.path.join(results_path, '{}.h5'.format(full_basin))
        key = attr_id.replace(' ', '_')
        df = pd.read_hdf(path, key=key)

        for i, scenario in basin_scenarios:
            ensemble_names = ENSEMBLE_NAMES[basin][scenario['name']]
            df.columns.set_levels(ensemble_names, level=i + 2, inplace=True)

    if filterby:
        resources = [s.replace('_', ' ') for s in filterby]
        idx = pd.IndexSlice
        df = df.loc[:, idx[:, resources]]

    if df.empty:
        return None

    if aggregate:
        df = agg_by_resources(df, aggregate)

    df *= multiplier

    return df
