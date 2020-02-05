import os
import pandas as pd


def wyt_below_friant(root_path, scenarios, filename):
    thresholds_taf = [0, 400, 670, 930, 1450, 2500]

    for scenario in scenarios:

        inpath = os.path.join(root_path, scenario, filename)

        df = pd.read_csv(inpath, index_col=0, header=0, squeeze=True)

        wyts = []
        for row in df:
            wyt = sum([1 for i in thresholds_taf if row > i * 1.2335])
            wyts.append(wyt)

        df2 = pd.DataFrame(data=wyts, index=df.index, columns=['WYT'])

        outpath = os.path.join(root_path, scenario, 'SJ restoration flows WYT.csv')
        df2.to_csv(outpath)
