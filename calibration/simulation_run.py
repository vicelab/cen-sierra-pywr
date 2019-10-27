import numpy as np
import pandas as pd
import sys
import json

from tqdm import tqdm
from load_model import load_model


def evaluate_model(model_path, root_dir, bucket, network_key, parameters):
    # Changes JSON parameter to another value
    with open(model_path, "r") as f:
        data = json.load(f)

    parameters_csv = pd.read_csv("Stan_Model/input_csvs/parameters.csv")
    for index in range(0, len(parameters_csv)):
        data['parameters'][parameters_csv.iloc[index, 0]]['value'] = parameters[index]
    del parameters_csv

    with open(model_path, 'w') as f:
        json.dump(data, f, indent=2)

    # Create the model with a modified JSON
    model = load_model(root_dir, model_path, bucket=bucket, network_key=network_key)

    # initialize model
    model.setup()

    timesteps = range(len(model.timestepper))
    step = None

    # Runs model through time to create a time series output
    for step in tqdm(timesteps, ncols=80):
        try:
            model.step()
        except Exception as err:
            print('Failed at step {}'.format(model.timestepper.current))
            print(err)
            break

    # Extract the model's output that we want to calibrate
    results = model.to_dataframe()
    results.to_csv('results.csv')

    output = np.array([])
    simulation_csv = pd.read_csv("input_csvs/simulations.csv")
    for index in range(0, len(simulation_csv)):
        output = np.append(output, results[simulation_csv.iloc[index]])

    # Save time series data to a local file
    np.save("model_output.npy", output)

if __name__ == "__main__":
    # Saves passed in arguments as local variables
    model_path = sys.argv[1]
    root_dir = sys.argv[2]
    bucket = sys.argv[3]
    network_key = sys.argv[4]

    # Converts the string representation of the array to a float array
    # Ex: "[123, 234ll 3453]" ->  ["[123", "23411", "3453]"] -> [123, 23411, 34553]
    parameters = sys.argv[5].split(",")
    for index in range(0, len(parameters)):
        if index == 0:
            parameters[index] = parameters[index][1:]
        elif index == len(parameters)-1:
            parameters[index] = parameters[index][0:len(parameters[index])-1]
        parameters[index] = float(parameters[index][0:len(parameters[index])-1])

    evaluate_model(model_path, root_dir, bucket, network_key, parameters)
