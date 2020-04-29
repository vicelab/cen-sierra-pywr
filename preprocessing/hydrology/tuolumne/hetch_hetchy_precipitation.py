import os
import pandas as pd


def hh_precip_from_Livneh(metadata_path, sequence_name, source_path, dest_path):
    filepath = os.path.join(metadata_path, 'drought_sequences.csv')
    df = pd.read_csv(filepath, index_col=0, header=0)
    years = df.loc[sequence_name]

    filename = 'precipitation_Hetch_Hetchy_mm.csv'

    source_filepath = os.path.join(source_path, filename)
    source_precip = pd.read_csv(source_filepath, index_col=0, header=0, parse_dates=True)
    source_precip['WY'] = source_precip.index.map(lambda d: d.year if d.month < 10 else d.year + 1)

    df = pd.DataFrame()

    for year in years:
        try:
            y = int(year)
        except:
            continue # nan
        year_precip = source_precip[source_precip['WY']==y].drop('WY', axis=1)
        df = df.append(year_precip)

    outpath = os.path.join(dest_path, filename)
    df.to_csv(outpath)
