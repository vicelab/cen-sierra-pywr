# Data Preparation  
  
This section describes how to prepare (preprocess) data needed as input to the CSN model. An important assumption is that hydrologic and electricity price data is already prepared and stored in the correct file location, as described below. Note that input data is not stored in GitHub.

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

Each of the following scripts/modules must be run for each scenario, in order. Fortunately, many of these are aggregated into a single script: `./preprocessing/preprocess_all.py`. This script can be modified as needed, depending on the preprocessing needed (typically, not all preprocessing would be done at once).

### Step 1. Initial preprocessing

This script perform some necessary initial fixes to the hydrologic data before the main preprocessing can occur.

1. `scripts.usj.disaggregate_SJN_09_subwatershed`

### Step 2. Common preprocessing

These scripts/modules generally just reorganize and aggregate runoff data (e.g., into full natural flow)

1. `scripts.aggregate_subwatersheds`
1. `scripts.create_forecasted_hydrology`
1. `scripts.create_full_natural_flow`

### Step 3. Basin preprocessing

These scripts/modules convert runoff data into derivative data for specific basins. Currently there are no hydrology preprocessing steps for the Tuolumne River.

* Stanislaus

  1. `scripts.full_natural_flow_exceedance_forecast`
  1. `stanislaus/calculate_WYT_P2005_P2130.py`
  1. `stanislaus/calculate_WYT_P2019.py`
  1. `stanislaus/calculatePeakFlowDonnellsLake.R` (to be converted to Python)

* Merced

  1. `merced/calculateExchequerWYT.py`

* Upper San Joaquin

  1. `scripts.usj.sjrrp_below_friant`
  1. `upper_san_joaquin\calculateInflowToMillertonLake_AprToJul.R` (to be converted to Python)

## Electricity prices

[to-be-filled]

## Management

These files/scripts are used to prepare input data other than hydrology and electricity price data, and are specific to each basin.

[to-be-filled]

## Data creation script lookup table

The following table lists which file/script is used to create each dataset needed to run the model. Note that this is only for the base runs, not alternative management scenarios.

| Data                                       | Script                                                        |
| :----------------------------------------- | :------------------------------------------------------------ |
| `runoff_aggregated`                        | `scripts.aggregate_subwatersheds`                             |
| `runoff_monthly_forecasts`                 | `scripts.create_forecasted_hydrology`                         |
| `full_natural_flow_daily_mcm.csv`          | `scripts.create_full_natural_flow`                            |
| `full_natural_flow_monthly_mcm.csv`        | `scripts.create_full_natural_flow`                            |
| `full_natural_flow_annual_mcm.csv`         | `scripts.create_full_natural_flow`                            |
| `Exchequer_WYT.csv`                        | `merced/calculateExchequerWYT.py`                             |
| `fnf_forecast_mcm.csv`                     | `scripts.full_natural_flow_exceedance_forecast`               |
| `WYT_P2005_P2130.csv`                      | `stanislaus/calculate_WYT_P2005_P2130.py`                     |
| `WYT_P2019.csv`                            | `stanislaus/calculate_WYT_P2019.py`                           |
| `peak_runoff_DonnellsRes_MarToMay_cms.csv` | `stanislaus/calculatePeakFlowDonnellsLake.R`                  |
| `SJ restoration flows.csv`                 | `scripts.usj.sjrrp_below_friant`                              |
| `inflow_MillertonLake_AprToJul_AF.csv`     | `upper_san_joaquin/calculateInflowToMillertonLake_AprToJul.R` |
