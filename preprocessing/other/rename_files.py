import os
import pandas as pd
import shutil

root_dir = r'C:\Users\david\Box\CERC-WET\Task7_San_Joaquin_Model\Pywr models\results\full run'
for basin in ['stanislaus']:
    basin_path = os.path.join(root_dir, basin)
    scenarios = os.listdir(basin_path)
    for scenario in scenarios:
        scenario_path = os.path.join(basin_path, scenario)
        path1 = os.path.join(scenario_path, 'Output_Flow_mcm.csv')
        path2 = os.path.join(scenario_path, 'Output_Outflow_mcm.csv')
        if os.path.exists(path2):
            if os.path.exists(path1):
                df1 = pd.read_csv(path1, index_col=0, parse_dates=True, header=0)
                df2 = pd.read_csv(path2, index_col=0, parse_dates=True, header=0)
                pd.concat([df1, df2], axis=1).to_csv(path1)
            else:
                shutil.copy(path2, path1)
            os.remove(path2)



