import os
import pandas as pd


def convert_cms_to_mcm(src, dst):
    """
    This function converts the original bias corrected csv files from cms to mcm.
    Note that the original filenames did not include zero-padded basin numbers,
    so this script adds the zero padding, and saves the converted data in order by
    new filename.

    :param src:
    :param dst:
    :return:
    """

    dfs = {}
    for filename in os.listdir(src):
        if '.csv' in filename:
            inpath = os.path.join(src, filename)
            df = pd.read_csv(inpath, index_col=0, parse_dates=True, header=0) * 0.0864

            basin_number = int(os.path.splitext(filename)[0].split('sb')[-1])
            new_filename = 'tot_runoff_sb{:02}_mcm.csv'.format(basin_number)
            dfs[new_filename] = df

    filenames = sorted(dfs.keys())
    for filename in filenames:
        df = dfs.pop(filename)
        outpath = os.path.join(dst, filename)
        df.to_csv(outpath)
