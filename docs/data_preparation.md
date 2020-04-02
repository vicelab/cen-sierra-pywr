# Data Preparation  

**TL;DR** (internet speak for summary...):
1. set the `SIERRA_DATA_PATH` environment variable to the main model data folder.
2. run the following two scripts:
    1. `./preprocessing/preprocess_hydrology.py`
    1. `./preprocessing/preprocess_energy_prices.py`

## Overview

This section describes how to prepare (preprocess) data needed as input to the CSN model. An important assumption is that hydrologic and electricity price data is already prepared and stored in the correct file location, as described below. Note that input data is not stored in GitHub.

Preprocessing tasks vary in scope, including:

* all basins  
* some basins  
* specific basins

Preprocessing is done in several ways:

* by manually modifying an Excel file
* by running a standalone script (either Python or R)
* by running a Python module from within a Python script

Over time, these will converge toward the latter method, since it can be automated and standardized.

Below, the data directory structure is described, followed by preprocessing steps for each of hydrology and energy prices.

## Data directory structure  

The data structure is generally as follows. However, because each basin is run independently, the data structure can be varied on a per-basin basis (though should as a matter of practice follow this structure).  

**IMPORTANT**: This data folder is specified both in the main Pywr model and in preprocessing scripts via the `SIERRA_DATA_PATH` environment variable; this variable should be set first.

Note that in the following structure, only folders are listed, not files within these folders.  

```
data
├── common
    ├── scenarios
        ├── [scenario]
    ├── energy prices
├── [basin] (e.g., "Merced River")
    ├── gauges
    ├── management
    |   ├── BAU ("business-as-usual")
    |       ├── demand
    |       ├── flood control
    |       ├── IFRs
    ├── scenarios (i.e., climate scenarios)
        ├── [scanario]
            ├── preprocessed
            ├── runoff
            ├── runoff_aggregated
            ├── runoff_monthly_forecasts
 ```

Notes:

* `/common`: This folder includes data shared across all basins, including:

  * energy price data  
  * San Joaquin Valley Index data

* `/management`: This folder includes non-climate scenario data (demand, flood control, etc.).  

* `/scenarios`: Each subfolder within the `/scenarios` folder includes one folder for each named scenario. Furthermore, each named scenario folder contains the actual data files (typically .csv files) needed for that scenario. For example: `/scenarios/Livneh/runoff/tot_runoff_sb01_mcm.csv` for runoff data for subbasin 01 in that basin's folder.

## Hydrologic data ("scenarios")

All hydrologic data stems from the original runoff data stored in:  
`/[basin]/scenarios/[scenario]/runoff`

Each of the following scripts/modules must be run for each scenario, in order. Fortunately, many of these are aggregated into a single script: `./preprocessing/preprocess_hydrology.py`. This script can be modified as needed, depending on the preprocessing needed (typically, not all preprocessing would be done at once).

### Step 1. Initial preprocessing

This script perform some necessary initial fixes to the hydrologic data before the main preprocessing can occur.

1. `upper_san_joaquin.disaggregate_SJN_09_subwatershed`

### Step 2. Common preprocessing

These scripts/modules generally just reorganize and aggregate runoff data (e.g., into full natural flow)

1. `common.aggregate_subwatersheds`
1. `common.create_forecasted_hydrology`
1. `common.create_full_natural_flow`

### Step 3. Basin preprocessing

These scripts/modules convert runoff data into derivative data for specific basins. Currently there are no hydrology preprocessing steps for the Tuolumne River.

* Stanislaus

  1. `common.full_natural_flow_exceedance_forecast`
  1. `stanislaus.calculate_WYT_P2005_P2130`
  1. `stanislaus.calculate_WYT_P2019`
  1. `stanislaus.calculate_peak_donnell_lake_inflow`

* Merced

  1. `merced.calculate_Exchequer_WYT`

* Upper San Joaquin

  1. `upper_san_joaquin.sjrrp_below_friant`
  1. `upper_san_joaquin.millerton_snowmel_inflow` (to be converted to Python)

## Electricity prices

Electricity prices must be preprocessed for both the planning and scheduling models, as below. As with hydrology, these have been collected into a single script: `./preprocessing/preprocess_energy_prices.py`

  1. `energy_prices.linearize_prices` (linearize prices for planning model)
  1. `energy_prices.pivot_prices` (pivot prices for scheduling model)
  
A couple of points:
  1. Input to these functions are already within each respective folder, in a subfolder called `input`.
  1. There are some additional residual files in respective `output` subfolders. 

## Management

These files/scripts are used to prepare input data other than hydrology and electricity price data, and are specific to each basin.

[to-be-filled]

## Data creation script lookup table

The following table lists which file/script is used to create each dataset needed to run the model. Note that this is only for the base runs, not alternative management scenarios.

| Data                                       | Script                                                        |
| :----------------------------------------- | :------------------------------------------------------------ |
| `runoff_aggregated`                        | `common.aggregate_subwatersheds`                             |
| `runoff_monthly_forecasts`                 | `common.create_forecasted_hydrology`                         |
| `full_natural_flow_daily_mcm.csv`          | `common.create_full_natural_flow`                            |
| `full_natural_flow_monthly_mcm.csv`        | `common.create_full_natural_flow`                            |
| `full_natural_flow_annual_mcm.csv`         | `common.create_full_natural_flow`                            |
| `Exchequer_WYT.csv`                        | `merced.calculate_Exchequer_WYT.py`                             |
| `exceedance_forecast_mcm.csv`                     | `common.full_natural_flow_exceedance_forecast`               |
| `WYT_P2005_P2130.csv`                      | `stanislaus.calculate_WYT_P2005_P2130`                     |
| `WYT_P2019.csv`                            | `stanislaus.calculate_WYT_P2019`                           |
| `Donnells_Reservoir_Peak_MAM_Runoff_date.csv` | `stanislaus.calculate_peak_donnell_lake_inflow`                  |
| `SJ restoration flows.csv`                 | `upper_san_joaquin.sjrrp_below_friant`                              |
| `inflow_MillertonLake_AprToJul_mcm.csv`     | `upper_san_joaquin.calculate_millerton_snowmelt_inflow` |
