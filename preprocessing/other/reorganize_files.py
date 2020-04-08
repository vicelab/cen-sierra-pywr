import os
from shutil import move

for basin in ['merced', 'tuolumne', 'upper san joaquin', 'stanislaus']:
    scenarios_path = '{}/{} River/scenarios'.format(os.environ['SIERRA_DATA_PATH'], basin.title())
    variables_path = os.path.join(scenarios_path, 'runoff')
    for scenario in os.listdir(variables_path):
        scenario_path = os.path.join(variables_path, scenario)
        new_variable_path = os.path.join(scenarios_path, scenario, 'runoff')
        if not os.path.exists(new_variable_path):
            os.makedirs(new_variable_path)
        for filename in os.listdir(scenario_path):
            src = os.path.join(scenario_path, filename)
            dst = os.path.join(new_variable_path, filename)
            move(src, dst)