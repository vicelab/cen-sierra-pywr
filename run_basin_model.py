import os
import sys
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm


def load_model(root_dir, model_path, bucket=None, network_key=None, check_graph=False):
    os.chdir(root_dir)

    # needed when loading JSON file
    root_path = 's3://{}/{}/'.format(bucket, network_key)
    os.environ['ROOT_S3_PATH'] = root_path

    # Step 1: Load and register policies
    sys.path.insert(0, os.getcwd())
    policy_folder = '_parameters'
    for filename in os.listdir(policy_folder):
        if '__init__' in filename:
            continue
        policy_name = os.path.splitext(filename)[0]
        policy_module = '.{policy_name}'.format(policy_name=policy_name)
        # package = '.{}'.format(policy_folder)
        import_module(policy_module, policy_folder)

    modules = [
        ('.IFRS', 'policies'),
        ('.domains', 'domains')
    ]
    for name, package in modules:
        try:
            import_module(name, package)
        except Exception as err:
            print(' [-] WARNING: {} could not be imported from {}'.format(name, package))
            print(type(err))
            print(err)

    # Step 2: Load and run model
    ret = Model.load(model_path, path=model_path)
    return ret


def run_model(basin, network_key):
    root_dir = os.path.join(os.getcwd(), basin)
    bucket = 'openagua-networks'
    model_path = os.path.join(root_dir, 'pywr_model.json')
    model = load_model(root_dir, model_path, bucket=bucket, network_key=network_key)

    # initialize model
    model.setup()

    timesteps = range(len(model.timestepper))
    step = None

    # run model
    # note that tqdm + step adds a little bit of overhead.
    # use model.run() instead if seeing progress is not important

    for step in tqdm(timesteps, ncols=80):
        try:
            model.step()
        except Exception as err:
            print('\nFailed at step {}'.format(model.timestepper.current))
            print(err)
            # continue
            break

    # save results to CSV

    results = model.to_dataframe()
    results.columns = results.columns.droplevel(1)
    results_path = './results'
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    results.to_csv(os.path.join(results_path, 'system'))
    attributes = {}
    for c in results.columns:
        attribute = c.split('/')[-1]
        if attribute in attributes:
            attributes[attribute].append(c)
        else:
            attributes[attribute] = [c]
    for attribute in attributes:
        path = os.path.join(results_path, '{}.csv'.format(attribute))
        df = results[attributes[attribute]]
        df.columns = [c.split('/')[-2] for c in df.columns]
        df.to_csv(path)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--basin", help="Basin to run")
parser.add_argument("-nk", "--network_key", help="Network key")
args = parser.parse_args()

basin = args.basin
network_key = args.network_key or os.environ.get('NETWORK_KEY')

run_model(basin, network_key)

print('done!')
