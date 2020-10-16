import os
import pandas as pd

FLOW_HEADER = 'flow (mcm)'

def get_water_years(dates):
    return list(map(lambda d: d.year if d.month <= 9 else d.year + 1, dates))

def generate_data_from_sequence(basin, variable, seq_values, basin_dir, sequence_dir, debug=False):

    if not os.path.exists(sequence_dir):
        os.makedirs(sequence_dir)

    # loop through subwatersheds
    filenames = os.listdir(os.path.join(basin_dir, 'hydrology', 'historical', 'Livneh', variable))
    for filename in filenames:

        climate_data_lookup = {}

        df2 = pd.DataFrame()

        # loop through sequence values
        for i, seq_value in enumerate(seq_values):
            gcm, rcp, year = seq_value.split('_')
            year = int(year)

            # get source data
            df = climate_data_lookup.get((gcm, rcp))
            if df is None:
                climate = '_'.join([gcm, rcp])
                climate_dir = os.path.join(basin_dir, 'hydrology', 'gcms', climate, variable)
                filepath = os.path.join(climate_dir, filename)
                df = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True, names=[FLOW_HEADER])
                df['WY'] = get_water_years(df.index)
                climate_data_lookup[(gcm, rcp)] = df

            year_df = df[df['WY'] == year][FLOW_HEADER].copy()
            start_year = 2000 + i
            start_date = '{}-10-01'.format(start_year)
            end_date = '{}-09-30'.format(start_year + 1)
            idx = pd.date_range(start_date, end_date)

            # account for leap years by adding/deleting days at end of year
            if len(year_df) < len(idx):
                year_df.index = idx[:len(year_df)]
                year_df[idx[-1]] = year_df.iloc[-1]
            elif len(year_df) > len(idx):
                year_df.pop(year_df.index[-1])
                year_df.index = idx
            else:
                year_df.index = idx
            df2 = df2.append(year_df.to_frame())

        df2.index.name = 'date'
        outpath = os.path.join(sequence_dir, filename)
        df2.to_csv(outpath)

    return
