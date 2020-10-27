
# Code description --------------------------------------------------------

# This code is used to import the functional flow metrics developed by Yarnell et al. (2020) and apply them to the rim dams in the four study basins: Stanislaus, Tuolumne, Merced, and San Joaquin. First, the code will be developed for the Merced because it has the simplest network; then it can be adapted for the other study basins.


# Libraries ---------------------------------------------------------------

library(tidyverse)
library(plotly)

# Load data ---------------------------------------------------------------

all_basins_func_flows <- read_csv("functional_flows/TNC_ffm_2823750tuol_348435stan_21607271mer_19791955sj.csv")

#Stanislaus, Tuolumne, and San Joaquin units are mcm (cubic meters per minute). Merced units are cfs (cubic feet per second)
Stanislaus_unimpaired_flow <- read_csv("functional_flows/Stanislaus_full_natural_flow_daily_mcm.csv")

Tuolumne_unimpaired_flow <- read_csv("functional_flows/Tuolumne_full_natural_flow_daily_mcm.csv")

Merced_unimpaired_flow <- read_csv("functional_flows/Merced_full_natural_flow_daily_cfs.csv")

SJ_unimpaired_flow <- read_csv("functional_flows/SJ_full_natural_flow_daily_mcm.csv")

# Parse functional flows to individual basin --------------------------------------

Stanislaus_func_flow <- all_basins_func_flows %>% 
  filter(comid == "348435")

Tuolumne_func_flow <- all_basins_func_flows %>% 
  filter(comid == "2823750")

Merced_func_flow <- all_basins_func_flows %>% 
  filter(comid == "21607271")

SJ_func_flow <- all_basins_func_flows %>% 
  filter(comid == "19791955")


# Convert units of unimpaired flow files ----------------------------------

# Unimpaired flow files for Tuolumne, Stanislaus, and San Joaquin are currently in mcm - need to convert to cfs to match the functional flow recommendations.

#Rename columns for clarity
Stanislaus_unimpaired_flow <- Stanislaus_unimpaired_flow %>% 
  rename("flow_mcm" = "flow")

Stanislaus_unimpaired_flow$flow_cfs <- Stanislaus_unimpaired_flow$flow_mcm*35.315/60

ggplotly(
  ggplot() +
    geom_line(data = Stanislaus_unimpaired_flow, aes(x=date, y=flow_cfs), color = "darkblue") +
    labs(title = "Stanislaus", x = "Date", y = "Unimpaired flow (cfs)")
)

#These flows seem really low for unimpaired flow at a rim dam. Need to confirm that this is both the correct gage and correct unit conversion.


# Plot Merced flows -------------------------------------------------------

#Rename columns for clarity

Merced_unimpaired_flow <- Merced_unimpaired_flow %>% 
  rename("flow_cfs" = "flow") 

ggplotly(
  ggplot() +
    geom_line(data = Merced_unimpaired_flow, aes(x=date, y=flow_cfs), color = "darkblue") +
    labs(title = "Merced River", x = "Date", y = "Unimpaired flow (cfs)")
)

#Add 40% flow to show SWRCB proposal
Merced_unimpaired_flow$FNF_40_percent <- Merced_unimpaired_flow$flow_cfs*0.4

ggplotly(
  ggplot() +
    geom_line(data = Merced_unimpaired_flow, aes(x=date, y=flow_cfs), color = "darkblue") +
    geom_line(data = Merced_unimpaired_flow, aes(x=date, y=FNF_40_percent), color = "sienna3") +
    labs(title = "Merced River", x = "Date", y = "Flow (cfs)")
)

#Round to 2 decimal places in functional flow data for better labelling
Merced_func_flow$p10 <- round(Merced_func_flow$p10,digits = 2)
Merced_func_flow$p25 <- round(Merced_func_flow$p25,digits = 2)
Merced_func_flow$p50 <- round(Merced_func_flow$p50,digits = 2)
Merced_func_flow$p75 <- round(Merced_func_flow$p75,digits = 2)
Merced_func_flow$p90 <- round(Merced_func_flow$p90,digits = 2)

### NEXT STEPS: look at the timing metrics to define a functional flow schedule, then add to the plot. Josh suggests looking at water years 76-77 drought, 83 wet year, 97 flood year, and 2006/2011 wet years
