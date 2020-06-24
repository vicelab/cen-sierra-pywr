import os
import pandas as pd

FLOW_HEADER = 'flow (mcm)'


def generate_data_from_sequence(df, basin, sequence_name, basin_dir, sequence_dir):
    print(basin, sequence_name)

    sequence = df.loc[sequence_name].values

    if not os.path.exists(sequence_dir):
        os.makedirs(sequence_dir)
    water_years = None
    for filename in os.listdir(basin_dir):
        filepath = os.path.join(basin_dir, filename)
        df = pd.read_csv(filepath, index_col=0, header=0, parse_dates=True, names=[FLOW_HEADER])

        if water_years is None:
            water_years = list(map(lambda d: d.year if d.month <= 9 else d.year + 1, df.index))
        df['WY'] = water_years
        df2 = pd.DataFrame()
        for i, year in enumerate(sequence):
            try:
                year = int(year)
            except:
                continue
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
