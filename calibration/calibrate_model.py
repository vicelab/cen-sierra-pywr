import spotpy
from .spot_setup import SpotSetup

# Set local storage variables for calibration ie: Name and Format(CSV, RAM)
results_path = "../stanislaus/results/"
dbname = "temp_db"
dbformat = "csv"

rep = 4
results = []
spot_setup = SpotSetup(results_path)

# Setup the environment with a markov chain monte carlo algorithm
sampler = spotpy.algorithms.lhs(spot_setup, dbformat=dbformat, dbname=dbname)

# Calibrate the model over "rep" iterations
sampler.sample(rep)
results.append(sampler.getdata())
