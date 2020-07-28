import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob

results_path = os.environ['SIERRA_RESULTS_PATH']
sequences_path = os.path.join(results_path, 'Sequences')
figures_path = os.path.join(results_path, 'figures', 'sequences')
if not os.path.exists(figures_path):
    os.makedirs(figures_path)


def read_csv(path):
    return pd.read_csv(path, index_col=0, header=0, parse_dates=True)


def create_annual_energy_csv(basins, csv_path):
    dfs = []

    for basin in basins:

        basin_full = basin.replace('_', ' ').title() + ' River'

        basin_path = os.path.join(sequences_path, basin, 'sequences')

        energy_csv = 'Hydropower_Energy_MWh.csv'
        # energy_files = os.path.join(basin_path, '*', energy_csv)

        # for f in glob(energy_files):
        #
        #     df = pd.read_csv(f)

        for sequence in os.listdir(basin_path):
            print('Processing {}'.format(sequence))
            seqid, years, scheme, number = sequence.split('_')

            if scheme == 'RAND':
                dry_years = -1
                wet_years = -1
            else:
                dry_years = int(scheme[1])
                wet_years = int(scheme[3])

            energy_csv_path = os.path.join(basin_path, sequence, energy_csv)

            df = read_csv(energy_csv_path)
            df = df.sum(axis=1).to_frame()
            df['wy'] = df.index.map(lambda d: d.year if d.month < 10 else d.year + 1)
            df = df.reset_index()
            del df['Date']
            df.columns = ['value', 'wy']
            df = df.groupby('wy').agg('sum').reset_index()
            df['basin'] = sequence
            df['number'] = int(number[1:])
            df['scheme'] = scheme
            df['dry_years'] = dry_years
            df['wet_years'] = wet_years
            df.columns = ['wy', 'value'] + list(df.columns[2:])
            df = df[['wy'] + list(df.columns[2:]) + ['value']]
            dfs.append(df)

    df = pd.concat(dfs)

    df.to_csv(csv_path, index=False)


def create_timeseries_plot(csv_path):
    df = pd.read_csv(csv_path, index_col=None, header=0)

    y_label = 'Energy (MWh)'
    x_label = 'Water Year'
    color = 'lightgrey'

    # combined
    # fig1, ax = plt.subplots(figsize=(7, 5))
    # sns.boxplot(data=df, x='scheme', y='value', ax=ax, color=color)
    # ax.set_ylabel(ylabel=energy_label)

    small_letters = 'abcde'

    fig2, axes = plt.subplots(5, 1, figsize=(7, 10), sharex='all')
    # titles = ['a) One wet year', 'b) Two wet years']
    ax = axes[0]
    df1 = df[df.scheme == 'RAND']
    sns.lineplot(x='wy', y='value', data=df1, ax=ax, legend=None)
    ax.set_ylabel(ylabel=y_label)
    ax.set_xlabel(xlabel=x_label)
    ax.set_title('a) Random')

    dry_years = [2, 3, 4, 5]
    for i in range(4):
        ax = axes[i + 1]
        df1 = df[df.dry_years == dry_years[i]]
        sns.lineplot(data=df1[df1.wet_years == 1], x='wy', y='value', color='red', ax=ax, legend=None)
        sns.lineplot(data=df1[df1.wet_years == 2], x='wy', y='value', color='green', ax=ax, legend=None)
        ax.set_ylabel(ylabel=y_label)
        ax.set_xlabel(xlabel=x_label)
        ax.set_title('{}) {} dry years'.format(small_letters[i+1], dry_years[i]))
    plt.tight_layout()
    #     ax.set_ylabel(energy_label)
    #     ax.set_xlabel('Scheme')
    #     ax.set_title(titles[i])

    # fig2_filename = 'annual_energy_boxplots_by_wet_years.png'
    # fig2_path = os.path.join(figures_path, fig2_filename)
    # fig2.savefig(fig2_path, dpi=300)

    plt.show()

    plt.close('all')

    return


def create_annual_energy_figure(csv_path):
    df = pd.read_csv(csv_path, index_col=None, header=0)

    energy_label = 'Annual energy (MWh)'
    color = 'lightgrey'

    # combined
    fig1, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x='scheme', y='value', ax=ax, color=color)
    ax.set_ylabel(ylabel=energy_label)
    fig1_filename = 'annual_energy_boxplots_combined.png'
    fig1_path = os.path.join(figures_path, fig1_filename)
    fig1.savefig(fig1_path, dpi=300)

    # separated
    fig2, axes = plt.subplots(1, 2, figsize=(10, 5))
    titles = ['a) One wet year', 'b) Two wet years']
    for i, wet_years in enumerate([1, 2]):
        ax = axes[i]
        df1 = df[(df.wet_years == wet_years) | (df.scheme == 'RAND')]
        sns.boxplot(data=df1, x='scheme', y='value', ax=ax, palette='RdBu_r')
        ax.set_ylabel(energy_label)
        ax.set_xlabel('Scheme')
        ax.set_title(titles[i])
    fig2_filename = 'annual_energy_boxplots_by_wet_years.png'
    fig2_path = os.path.join(figures_path, fig2_filename)
    fig2.savefig(fig2_path, dpi=300)

    plt.show()

    plt.close('all')

    return


if __name__ == '__main__':
    csv_path = './annual_energy_MWh.csv'

    # create_annual_energy_csv(['stanislaus'], csv_path)
    create_timeseries_plot(csv_path)
    # create_annual_energy_figure(csv_path)
