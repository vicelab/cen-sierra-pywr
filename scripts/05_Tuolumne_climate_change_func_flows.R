
# Code description --------------------------------------------------------

# This code is used to run the functional flow calculator on climate change hydrology in the Central Sierra tributaries and upper San Joaquin. Different codes will be used for each basin as there are multiple climate change simulations for each. This code is developed for the Tuolumne.


# Libraries ---------------------------------------------------------------

library(ffcAPIClient)
library(tidyverse)

# Load data ---------------------------------------------------------------

#comid and gage id to run functional flow calculator
Ann_token <- "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM"

tuol_comid <- 2823750
tuol_gage_id <- 11289650

#climate change hydrology, with gcm indicated as object suffix
tuol_access10_mcm <- read_csv("functional_flows/climate_change/Tuolumne/ACCESS1-0_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_canesm2_mcm <- read_csv("functional_flows/climate_change/Tuolumne/CanESM2_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_ccsm4_mcm <- read_csv("functional_flows/climate_change/Tuolumne/CCSM4_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_cesm1_bgc_mcm <- read_csv("functional_flows/climate_change/Tuolumne/CESM1-BGC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_cmcc_cms_mcm <- read_csv("functional_flows/climate_change/Tuolumne/CMCC-CMS_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_cnrm_cm5_mcm <- read_csv("functional_flows/climate_change/Tuolumne/CNRM-CM5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_gfdl_cm3_mcm <- read_csv("functional_flows/climate_change/Tuolumne/GFDL-CM3_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_hadgem2_cc_mcm <- read_csv("functional_flows/climate_change/Tuolumne/HadGEM2-CC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_hadgem2_es_mcm <- read_csv("functional_flows/climate_change/Tuolumne/HadGEM2-ES_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

tuol_miroc5_mcm <- read_csv("functional_flows/climate_change/Tuolumne/MIROC5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

# Unit conversion of gmc hydrology ----------------------------------------

# Climate change flow files are currently in mcm (million cubic meters per day) - need to convert to cfs to match the functional flow recommendations.

#Access1-0 gcm
tuol_access10_mcm <- tuol_access10_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_access10_mcm$flow_cfs <- tuol_access10_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_access10_cfs <- tuol_access10_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_access10_cfs$date <- as.character(tuol_access10_cfs$date)

#CanESM2 gcm
tuol_canesm2_mcm <- tuol_canesm2_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_canesm2_mcm$flow_cfs <- tuol_canesm2_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_canesm2_cfs <- tuol_canesm2_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_canesm2_cfs$date <- as.character(tuol_canesm2_cfs$date)

#CCSM4 gcm
tuol_ccsm4_mcm <- tuol_ccsm4_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_ccsm4_mcm$flow_cfs <- tuol_ccsm4_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_ccsm4_cfs <- tuol_ccsm4_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_ccsm4_cfs$date <- as.character(tuol_ccsm4_cfs$date)

#CESM1-BGC gcm
tuol_cesm1_bgc_mcm <- tuol_cesm1_bgc_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_cesm1_bgc_mcm$flow_cfs <- tuol_cesm1_bgc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_cesm1_bgc_cfs <- tuol_cesm1_bgc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_cesm1_bgc_cfs$date <- as.character(tuol_cesm1_bgc_cfs$date)

#CMCC-CMS gcm
tuol_cmcc_cms_mcm <- tuol_cmcc_cms_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_cmcc_cms_mcm$flow_cfs <- tuol_cmcc_cms_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_cmcc_cms_cfs <- tuol_cmcc_cms_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_cmcc_cms_cfs$date <- as.character(tuol_cmcc_cms_cfs$date)

#CNRM-CM5 gcm
tuol_cnrm_cm5_mcm <- tuol_cnrm_cm5_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_cnrm_cm5_mcm$flow_cfs <- tuol_cnrm_cm5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_cnrm_cm5_cfs <- tuol_cnrm_cm5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_cnrm_cm5_cfs$date <- as.character(tuol_cnrm_cm5_cfs$date)

#GFDL-CM3 gcm
tuol_gfdl_cm3_mcm <- tuol_gfdl_cm3_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_gfdl_cm3_mcm$flow_cfs <- tuol_gfdl_cm3_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_gfdl_cm3_cfs <- tuol_gfdl_cm3_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_gfdl_cm3_cfs$date <- as.character(tuol_gfdl_cm3_cfs$date)

#HadGEM2-CC gcm
tuol_hadgem2_cc_mcm <- tuol_hadgem2_cc_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_hadgem2_cc_mcm$flow_cfs <- tuol_hadgem2_cc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_hadgem2_cc_cfs <- tuol_hadgem2_cc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_hadgem2_cc_cfs$date <- as.character(tuol_hadgem2_cc_cfs$date)

#HadGEM2-ES gcm
tuol_hadgem2_es_mcm <- tuol_hadgem2_es_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_hadgem2_es_mcm$flow_cfs <- tuol_hadgem2_es_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_hadgem2_es_cfs <- tuol_hadgem2_es_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_hadgem2_es_cfs$date <- as.character(tuol_hadgem2_es_cfs$date)

#MIROC5 gcm
tuol_miroc5_mcm <- tuol_miroc5_mcm %>% 
  rename("flow_mcm" = "flow")

tuol_miroc5_mcm$flow_cfs <- tuol_miroc5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

tuol_miroc5_cfs <- tuol_miroc5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

tuol_miroc5_cfs$date <- as.character(tuol_miroc5_cfs$date)

# Observed functional flows ------------------------------------------------

ffc <- FFCProcessor$new()  # make a new object we can use to run the commands

# configure the object and run CEFF step 1 plus outputs

ffc$step_one_functional_flow_results(gage_id=tuol_gage_id,
                                     token=Ann_token,
                                     output_folder = "functional_flows/Tuolumne")

# Climate change functional flows -----------------------------------------

ffc_cc <- FFCProcessor$new() #make a new object to run the functional flows for climate change hydrology

ffc_cc$flow_field <- "flow_cfs"

ffc_cc$date_format_string <- "%Y-%m-%d"

ffc_cc$timeseries_enable_filtering <- FALSE #we can do this because the filter step showed us that there were no NAs


# ACCESS1-0 functional flows ----------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_access10_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/ACCESS1-0_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()


# CanESM2 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_canesm2_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/CanESM2_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CCSM4 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_ccsm4_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/CCSM4_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CESM1-BGC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_cesm1_bgc_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/CESM1-BGC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CMCC-CMS functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_cmcc_cms_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/CMCC-CMS_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CNRM-CM5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_cnrm_cm5_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/CNRM-CM5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# GFDL-CM3 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_gfdl_cm3_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/GFDL-CM3_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()
# HadGEM2-CC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_hadgem2_cc_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/HadGEM2-CC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# HadGEM2-ES functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_hadgem2_es_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/HadGEM2-ES_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# MIROC5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = tuol_miroc5_cfs, 
                                        token=Ann_token, 
                                        comid=tuol_comid,
                                        output_folder = "functional_flows/climate_change/Tuolumne/MIROC5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()