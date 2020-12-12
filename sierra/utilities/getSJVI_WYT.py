import datetime
import pandas as pd

SJVI_types = pd.read_csv("s3_imports/SJVI.csv", index_col=0, header=0, parse_dates=False,
                              squeeze=True)
start_time = datetime.datetime(1980, 10, 1)
length = SJVI_types.shape[0]-1

def getSJVI_WYT(timestep):
    for year in list(range(start_time.year, start_time.year + length, 1)):
        if datetime.datetime(year, 10, 1) <= timestep.datetime <= datetime.datetime(year+1, 9, 30):
            SJVI_value = SJVI_types[year+1]
            if SJVI_value <= 2.1:
                year_type = 1  # "Critical"
            elif SJVI_value <= 2.8:
                year_type = 2  # "Dry"
            elif SJVI_value <= 3.1:
                year_type = 3  # "Below"
            elif SJVI_value <= 3.8:
                year_type = 4  # "Above"
            else:
                year_type = 5  # "Wet"
            return year_type

    return None
