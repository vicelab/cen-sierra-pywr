# Data Preparation  
  
This section describes how to prepare (preprocess) data needed as input to the CSN model. An important assumption is that hydrologic and electricity price data is already prepared and stored in the correct file location, as described below.

Preprocessing tasks vary in scope, including:

* all basins  
* some basins  
* specific basins

Preprocessing is done in several ways:

* by manually modifying an Excel file
* by running a standalone script (either Python or R)
* by running a Python module from within a Python script

Over time, these will converge toward the latter two methods, since they can be automated and standardized.

Below, the data directory structure is described, followed by preprocessing steps for each of hydrology and electricity prices.

## Data directory structure  

The data structure is generally as follows. However, because each basin is run independently, the data structure can be varied on a per-basin basis (though should as a matter of practice follow this structure).  

Note that in the following structure, only folders are listed, not files within these folders.  

```
data
├── common
├── [basin] (e.g., "Merced River")
    ├── gauges
    ├── management
    |   ├── BAU ("business-as-usual")
    |       ├── demand
    |       ├── flood control
    |       ├── IFRs
    ├── scenarios (climate scenarios)
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

* `/scenarios`: Each subfolder within the `\scenarios` folder includes one folder for each named scenario. Furthermore, each named scenario folder contains the actual data files (typically .csv files) needed for that scenario. For example: `/scenarios/runoff/Livneh/tot_runoff_sb01_mcm.csv` for runoff data for subbasin 01 in that basin's folder.

## Hydrologic data

All hydrologic data stems from the original runoff data stored in:  
`/[basin]/scenarios/runoff/[scenario name]/`

Each of the following scripts/modules must be run for each scenario, in order. Fortunately, many of these are aggregated into a single script: `./preprocessing/preprocess_all.py`. This script can be modified as needed, depending on the preprocessing needed (typically, not all preprocessing would be done at once).

### Initial preprocessing

1. `scripts.usj.disaggregate_SJN_09_subwatershed`: This script disaggregates runoff runoff from the SJN_09 subwatershed in the Upper San Joaquin basin into four subcatchments.

### Primary preprocessing

These scripts/modules generally just reorganize and aggregate runoff data (e.g., into full natural flow)

1. `scripts.aggregate_subwatersheds`
1. `scripts.create_forecasted_hydrology`
1. `scripts.create_full_natural_flow`

### Derivative preprocessing

These scripts/modules convert runoff data into derivative data (e.g., exceedance forecasts)

* All

  1. `scripts.full_natural_flow_exceedance_forecast`

* Upper San Joaquin

  1. `scripts.usj.sjrrp_below_friant`

## Electricity prices

[to-be-filled]

## Data creation script lookup table

The following table lists which file/script is used to create each dataset needed to run the model. Note that this is only for the base runs, not alternative management scenarios.

| Data                       | Script                                          |
| :------------------------- | :---------------------------------------------- |
| `runoff_aggregated`        | `scripts.aggregate_subwatersheds`               |
| `runoff_monthly_forecasts` | `scripts.full_natural_flow_exceedance_forecast` |
