import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

ANALYSIS = 'MIDH2O'

res_dir_all = os.environ['SIERRA_RESULTS_PATH']
res_dir = os.path.join(res_dir_all, ANALYSIS, 'merced', 'historical', 'Livneh')

out_dir = os.path.join(res_dir_all, '..', 'analyses', ANALYSIS)

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# main analisis - basic graphs

filename = 'Hydropower_Energy_MWh.csv'
filepath = os.path.join(res_dir, filename)

df = pd.read_csv(filepath, header=[0,1], index_col=0, parse_dates=True)

df.plot()
plt.show()

print('done!')