import os
from datetime import date
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

input_dir = os.environ['SIERRA_DATA_PATH']
# output_dir = os.environ['SIERRA_RESULTS_PATH']

# prices
prices_path = Path(input_dir, r'common\energy prices\prices_pivoted_select_years.csv')
s = pd.read_csv(prices_path, index_col=0, header=0, parse_dates=True).mean(axis=1)
s = s[s.index.year == 2009]
s_oct_dec = s[s.index.month >= 10].values
s_jan_sep = s[s.index.month <= 9].values
idx_oct_dec = [date(d.year - 1, d.month, d.day) for d in s.index if d.month >= 10]
idx_jan_sep = [date(d.year, d.month, d.day) for d in s.index if d.month <= 9]
dates = idx_oct_dec + idx_jan_sep

prices = pd.Series(
    index=dates,
    data=np.concatenate((s_oct_dec, s_jan_sep))
)


def read_csv(path):
    start = '2004-10-01'
    end = '2005-09-30'
    df = pd.read_csv(path, index_col=0, header=0, parse_dates=True)[start:end]
    df.index = prices.index
    return df


# full natural flow
fnf_path = Path(input_dir, r'Upper San Joaquin River\hydrology\historical\Livneh\preprocessed',
                'full_natural_flow_daily_mcm.csv')
fnf = read_csv(fnf_path)


def get_energy_df(study):
    path = Path('../../results', study, 'upper_san_joaquin/historical/Livneh', 'Hydropower_Energy_MWh.csv')
    df = read_csv(path)
    df = df.sum(axis=1) / 1000
    return df


# hydropower
hp_no_planning = get_energy_df('usj - no planning')
hp_planning = get_energy_df('usj - planning')

# figure
fig, axes = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(8, 5))

# top
ax0 = axes[0]
ax0.plot(prices, color='black')
ax0.set_ylabel('Price ($/MWh)')

# bottom
ax1 = axes[1]
ax1.plot(hp_no_planning)
ax1.plot(hp_planning)
ax1.set_ylim(0, 60)
ax1.set_ylabel('Generation (GWh/day)')

ax2 = ax1.twinx()
ax2.plot(fnf)
ax2.set_ylim(0, 60)
ax2.set_ylabel('Flow (mcm/day)')

ax0.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
for ax in [ax1, ax2]:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b, %Y'))

# rotate and align the tick labels so they look better
fig.autofmt_xdate()

plt.show()
