import os
import spotpy
import pandas as pd
import numpy as np
import subprocess
import json

from spotpy.objectivefunctions import rmse

class SpotSetup(object):

    def parameters(self):
        # Generates a random param value based on the self.params
        return spotpy.parameter.generate(self.params)

    def __init__(self, results_path, used_algorithm='default'):
        self.results_path = results_path
        self.model_name = results_path.split("/")[1]
        self.used_algorithm = used_algorithm
        self.nodes = pd.read_csv("inputs/nodes.csv")
        # Generating Parameter Values via CSV
        parameters_csv = pd.read_csv("inputs/parameters.csv")
        self.params = []
        for index in range(0, len(parameters_csv)):
            self.params.append(spotpy.parameter.Uniform(parameters_csv.iloc[index, 0],
                                                        parameters_csv.iloc[index, 1],
                                                        parameters_csv.iloc[index, 2],
                                                        parameters_csv.iloc[index, 3]))
        del parameters_csv

        # Generating Evaluation Data via CSV
        self.evaluation_data = np.array([])
        results = pd.read_csv(results_path + "observed storage.csv")
        for index in range(0, len(self.nodes)):
            self.evaluation_data = np.append(self.evaluation_data, results[self.nodes.iloc[index]][1:])

    def simulation(self, vector):

        print("Trying parametre: {}".format(vector))

        # Change the JSON in File
        parameters = []
        for parameter in vector:
            parameters.append(parameter)

        with open("../{}/pywr_model.json".format(self.model_name), "r") as f:
            data = json.load(f)

        parameters_csv = pd.read_csv("inputs/parameters.csv")
        for index in range(0, len(parameters_csv)):
            data['parameters'][parameters_csv.iloc[index, 0]]['value'] = parameters[index]
        del parameters_csv

        with open("../{}/pywr_model.json".format(self.model_name), 'w') as f:
            json.dump(data, f, indent=2)

        # Run the model using run_basin_model
        proc = subprocess.run(['python', '../run_basin_model.py', "-b {}".format(self.model_name), '-t calibrate'])

        # Save the output from the model running
        # Join all results tables together
        results_csv = pd.read_csv(self.results_path + "storage.csv")

        output = np.array([])
        for index in range(0, len(results_csv)):
            output = np.append(output, results_csv[self.nodes.iloc[index]])

        return output

    def evaluation(self):
        # Returns the observed data
        return self.evaluation_data

    def objectivefunction(self, simulation, evaluation):
        evaluation_input = np.array([])
        # Get rid of the impact of NULL values in the evaluation data
        for index in range(0, len(simulation)):
            if not evaluation[index]:
                evaluation_input = np.append(evaluation_input, simulation[index])
            else:
                evaluation_input = np.append(evaluation_input, evaluation[index])
        # Generates a minimum objective value of the output
        objective_function = -rmse(evaluation=evaluation_input, simulation=simulation)

        print("Objective Value: {}".format(objective_function))
        return objective_function
