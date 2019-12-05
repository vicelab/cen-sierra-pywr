import os
from shutil import copyfile

for basin in ['stanislaus']:
    basin_path = '../../data/{} River/Scenarios'.format(basin.title())
    scenarios = os.listdir(basin_path)
    for scenario in scenarios:
        scenario_path = os.path.join(basin_path, scenario)
        variables = os.listdir(scenario_path)
        for variable in variables:
            variable_path = os.path.join(scenario_path, variable)
            new_variable_path = os.path.join(basin_path, variable, scenario)
            if not os.path.exists(new_variable_path):
                os.makedirs(new_variable_path)
            for filename in os.listdir(variable_path):
                copyfile(
                    os.path.join(variable_path, filename),
                    os.path.join(new_variable_path, filename)
                )