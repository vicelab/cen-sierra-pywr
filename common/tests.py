import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


def test_planning_model(model, save_results=True, months=12):
    start = model.timestepper.start
    end = model.timestepper.end

    dates = pd.date_range(start=start, end=end, freq='MS')  # MS = month start

    fn_tpl = 'monthly_{v}_S{level}.csv'

    # now = datetime.now()
    for date in tqdm(dates[:3], ncols=80, disable=True):
        model.reset(start=date)
        stepnow = datetime.now()
        model.step()
        # print((datetime.now() - stepnow).total_seconds())
        if save_results and date == dates[0]:
            monthly_dir = './results'
            df = model.to_dataframe().resample('M').max()
            df.columns = df.columns.droplevel(1)
            variables = set([c.split('/')[1] for c in df.columns])
            for v in variables:
                node_names = []
                month_numbers = []
                col_names = []
                for c in df.columns:
                    res_name, variable, month_str = c.split('/')
                    node_name = '/'.join([res_name, month_str])
                    if variable == v:
                        col_names.append(c)
                        node_names.append(res_name)
                        month_numbers.append(int(month_str))
                df_filtered = df[col_names]
                df_filtered.columns = pd.MultiIndex.from_arrays([node_names, month_numbers])
                df0 = df_filtered.stack(level=0)
                df1 = df_filtered.stack(level=1)
                path0 = os.path.join(monthly_dir, fn_tpl.format(v=v, level=0))
                path1 = os.path.join(monthly_dir, fn_tpl.format(v=v, level=1))
                df0.index.names = ['Start month', 'Resource']
                df0.to_csv(path0)
                df1.to_csv(path1)

                # plot
                for scope in ['all', 'w/o Melones']:
                    if scope == 'all':
                        cols = df1.columns
                    else:
                        cols = [c for c in df1.columns if 'melones' not in c.lower()]
                    dfp = df1[cols].iloc[0:months]
                    dfp.index = pd.DatetimeIndex(start=date, periods=months, freq='M')
                    dfp.index.name = 'Date'
                    title = 'Planning {} ({}): {}'.format(v, scope, date.strftime('%b %Y'))
                    fig, ax = plt.subplots(figsize=(10, 5))
                    dfp.plot(title=title, ax=ax)
                    ax.set_xlabel('Month')
                    ax.set_ylabel('{} (mcm)'.format(v.title()))
                    plt.tight_layout()
                    fig.savefig(os.path.join(monthly_dir, '{} {}.png'.format(v, scope.replace('/', ''))))
            plt.show()

    # print('\nRunning portion complete in {} seconds'.format((datetime.now() - now).total_seconds()))
    # print('...done')
    return
