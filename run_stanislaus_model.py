import os
import sys
import json
import pandas as pd
from pywr.core import Model
from importlib import import_module
from tqdm import tqdm
import matplotlib.pyplot as plt
from stanislaus_demo.parameters import WaterLPParameter
from stanislaus_demo.utilities.converter import convert

def get_cost(timestep, energy_data):
    x = 100  # Value to be adjusted
    totDemand = float(energy_data['TotDemand'][timestep])
    maxDemand = float(energy_data['MaxDemand'][timestep])
    minDemand = float(energy_data['MinDemand'][timestep])
    minVal = x * (totDemand / 768)  # 768 GWh is median daily energy demand for 2009
    maxVal = minVal * (maxDemand / minDemand)
    d = maxVal - minVal
    return [-(maxVal - d / 8), -(maxVal - 3 * d / 8), -(maxVal - 5 * d / 8), -(maxVal - 7 * d / 8)]

def convert_demand(data):
    # Modify this function to return the correct values
    TC = data/4
    TC = TC * 60*60*24
    return [TC, TC, TC, TC]

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


root_dir = os.path.join(os.getcwd(), 'stanislaus_demo')
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
path = 's3://{}/{}/'.format(bucket, network_key) + 'Scenarios/Livneh/energy_netDemand.csv'
energy_data = pd.read_csv(path, usecols=[0,1,2,3], index_col=0, header=None, names=['day','TotDemand','MaxDemand','MinDemand'], parse_dates=False)

for step in tqdm(timesteps, ncols=80):
    try:
        with open(model_path, "r") as f:
            data = json.load(f)

        tc_values = data["parameters"]["node/Donnells PH/Turbine Capacity"]["value"]
        data['nodes'][9]['costs'] = get_cost(step+1, energy_data)
        data['nodes'][9]['max_flows'] = convert_demand(tc_values)
        data["parameters"]["node/Donnells PH/Water Demand"]["value"] = sum(convert_demand(tc_values))

        with open(model_path, 'w') as f:
            json.dump(data, f, indent=2)
        model.step()
    except Exception as err:
        print('Failed at step {}'.format(model.timestepper.current))
        print(err)
        break

# save results to CSV
results = model.to_dataframe()
results.to_csv('results.csv')

# # plot Lake McClure storage
# fig, ax = plt.subplots(figsize=(16, 8))
# S = results['node/Lake McClure/storage']
# ax.plot(S.index, S)
# fig.show()
