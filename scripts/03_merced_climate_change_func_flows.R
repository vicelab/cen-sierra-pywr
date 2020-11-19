
# Code description --------------------------------------------------------

# This code is used to run the functional flow calculator on climate change hydrology in the Central Sierra tributaries and upper San Joaquin. Different codes will be used for each basin as there are multiple climate change simulations for each. This code is developed for the Merced.


# Libraries ---------------------------------------------------------------

library(ffcAPIClient)
library(tidyverse)
library(lubridate)

# Load data ---------------------------------------------------------------

#comid and gage id to run functional flow calculator
Ann_token <- "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM"

mer_comid <- 21607271
mer_gage_id <- 11270000

#climate change hydrology, with gcm indicated as object suffix
mer_access10_mcm <- read_csv("functional_flows/climate_change/Merced/ACCESS1-0_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_canesm2_mcm <- read_csv("functional_flows/climate_change/Merced/CanESM2_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_ccsm4_mcm <- read_csv("functional_flows/climate_change/Merced/CCSM4_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_cesm1_bgc_mcm <- read_csv("functional_flows/climate_change/Merced/CESM1-BGC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_cmcc_cms_mcm <- read_csv("functional_flows/climate_change/Merced/CMCC-CMS_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_cnrm_cm5_mcm <- read_csv("functional_flows/climate_change/Merced/CNRM-CM5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

mer_gfdl_cm3_mcm <- read_csv("functional_flows/climate_change/Merced/GFDL-CM3_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

# Unit conversion of gmc hydrology ----------------------------------------

# Climate change flow files are currently in mcm (million cubic meters per day) - need to convert to cfs to match the functional flow recommendations.

#Access1-0 gcm
mer_access10_mcm <- mer_access10_mcm %>% 
  rename("flow_mcm" = "flow")

mer_access10_mcm$flow_cfs <- mer_access10_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_access10_cfs <- mer_access10_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_access10_cfs$date <- as.character(mer_access10_cfs$date)

#CanESM2 gcm
mer_canesm2_mcm <- mer_canesm2_mcm %>% 
  rename("flow_mcm" = "flow")

mer_canesm2_mcm$flow_cfs <- mer_canesm2_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_canesm2_cfs <- mer_canesm2_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_canesm2_cfs$date <- as.character(mer_canesm2_cfs$date)

#CCSM4 gcm
mer_ccsm4_mcm <- mer_ccsm4_mcm %>% 
  rename("flow_mcm" = "flow")

mer_ccsm4_mcm$flow_cfs <- mer_ccsm4_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_ccsm4_cfs <- mer_ccsm4_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_ccsm4_cfs$date <- as.character(mer_ccsm4_cfs$date)

#CESM1-BGC gcm
mer_cesm1_bgc_mcm <- mer_cesm1_bgc_mcm %>% 
  rename("flow_mcm" = "flow")

mer_cesm1_bgc_mcm$flow_cfs <- mer_cesm1_bgc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_cesm1_bgc_cfs <- mer_cesm1_bgc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_cesm1_bgc_cfs$date <- as.character(mer_cesm1_bgc_cfs$date)

#CMCC-CMS gcm
mer_cmcc_cms_mcm <- mer_cmcc_cms_mcm %>% 
  rename("flow_mcm" = "flow")

mer_cmcc_cms_mcm$flow_cfs <- mer_cmcc_cms_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_cmcc_cms_cfs <- mer_cmcc_cms_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_cmcc_cms_cfs$date <- as.character(mer_cmcc_cms_cfs$date)

#CNRM-CM5 gcm
mer_cnrm_cm5_mcm <- mer_cnrm_cm5_mcm %>% 
  rename("flow_mcm" = "flow")

mer_cnrm_cm5_mcm$flow_cfs <- mer_cnrm_cm5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_cnrm_cm5_cfs <- mer_cnrm_cm5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_cnrm_cm5_cfs$date <- as.character(mer_cnrm_cm5_cfs$date)

#GFDL-CM3 gcm
mer_gfdl_cm3_mcm <- mer_gfdl_cm3_mcm %>% 
  rename("flow_mcm" = "flow")

mer_gfdl_cm3_mcm$flow_cfs <- mer_gfdl_cm3_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

mer_gfdl_cm3_cfs <- mer_gfdl_cm3_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

mer_gfdl_cm3_cfs$date <- as.character(mer_gfdl_cm3_cfs$date)

# Observed functional flows ------------------------------------------------

ffc <- FFCProcessor$new()  # make a new object we can use to run the commands

# configure the object and run CEFF step 1 plus outputs

ffc$step_one_functional_flow_results(gage_id=mer_gage_id,
                                     token=Ann_token,
                                     output_folder = "functional_flows/Merced")

# Climate change functional flows -----------------------------------------

ffc_cc <- FFCProcessor$new() #make a new object to run the functional flows for climate change hydrology

ffc_cc$flow_field <- "flow_cfs"

ffc_cc$date_format_string <- "%Y-%m-%d"

ffc_cc$timeseries_enable_filtering <- FALSE #we can do this because the filter step showed us that there were no NAs


# ACCESS1-0 functional flows ----------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_access10_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/ACCESS1-0_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()


# CanESM2 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_canesm2_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/CanESM2_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CCSM4 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_ccsm4_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/CCSM4_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CESM1-BGC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_cesm1_bgc_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/CESM1-BGC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CMCC-CMS functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_cmcc_cms_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/CMCC-CMS_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CNRM-CM5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_cnrm_cm5_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/CNRM-CM5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# GFDL-CM3 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = mer_gfdl_cm3_cfs, 
                                        token=Ann_token, 
                                        comid=mer_comid,
                                        output_folder = "functional_flows/climate_change/Merced/GFDL-CM3_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()