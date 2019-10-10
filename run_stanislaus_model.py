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


root_dir = os.path.join(os.getcwd(), 'san_joaquin')
bucket = 'openagua-networks'
model_path = os.path.join(root_dir, 'pywr_model.json')
network_key = os.environ.get('NETWORK_KEY')
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
results.to_csv(os.path.join(results_path, 'system.csv'))
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
    print(attribute)
    if attribute == 'flow':
        df2 = df[[c for c in df.columns if c[-3:] == ' PH']]
        path2 = os.path.join(results_path, 'powerhouse flow.csv')
        df2.to_csv(path2)

    df.to_csv(path)
