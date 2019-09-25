import pandas as pd
import os

tpl_in = "s3_imports/tot_runoff_sb{}.csv"
tpl_out = "data/tot_runoff_sb{:02}.csv"

for n in range(1,26):
    continue
    df = pd.read_csv(tpl_in.format(n), index_col=0)
    df *= 0.0864
    df.to_csv(tpl_out.format(n))

df = pd.read_csv("s3_imports/GaugeStreamFlow_cms_STNR.csv", index_col=0)
df *= 0.0864
df.to_csv("data/GaugesStreamflow_mcm.csv")

print('done!')
