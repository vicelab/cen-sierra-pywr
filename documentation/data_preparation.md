# Data Preparation

This section describes how to prepare data needed as input to the CSN model. Generally, this means preprocessing. An important assumption is that hydrologic and electricity price data is already prepared and stored in the correct file location, as described below.

Preprocessing tasks vary in scope, including:
* all basins
* some basins
* specific basins

## Directory structure

The data structure is generally as follows. However, because each basin is run independently, the data structure can be varied on a per-basin basis (though should as a matter of practice follow this structure).

Note that in the following structure, only folders are listed, not files within these folders.

```
/data
  /common
  /[basin] (e.g., "Merced River")
    /gauges
    /Management
      /BAU ("business-as-usual")
        /Demand
        /Flood Control
        /IFRs
    /Scenarios (climate scenarios)
      /preprocessed
      /runoff
      /runoff_aggregated
      /runoff_monthly_forecasts
```

Notes:
* `/common`: This folder includes data shared across all basins, including:
  * energy price data
  * San Joaquin Valley Index data
* `/Management`: This folder includes non-climate scenario data (demand, flood control, etc.).
* `/Scenarios`: This folder includes climate scenario data. Each subfolder within the `\scenarios` folder includes one folder for each named scenario. Furthermore, each named scenario folder contains the actual data files (typically .csv files) needed for that scenario. For example: `/scenarios/runoff/Livneh/tot_runoff_sb01_mcm.csv` for runoff data for subbasin 01 in that basin's folder.

## Original data storage location

Some original data is needed to create the input data files used in the model. These and their storage location include:

* Hydrologic data
`/[basin]/scenarios/runoff/[scenario name]/`

* Energy price data
`/common/energy prices/original`

## All basins
Note that where monthly data is produced, it is not needed/used for the Merced and Tuolumne basins.

### /preprocessed
* ``


### /runoff_aggregated


### /runoff_monthly_forecasts


## Specific basins

### Stanislaus

### Tuolumne

### Merced

### Upper San Joaquin 

## Electricity prices

# Scripts

preprocess_all.py: This runs one or more the following.

## Flood control

s1.py
* abc.csv
* xyz.csv
s2.py

## Ag. demand

etc.py
