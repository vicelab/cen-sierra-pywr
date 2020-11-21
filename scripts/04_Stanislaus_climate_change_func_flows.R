
# Code description --------------------------------------------------------

# This code is used to run the functional flow calculator on climate change hydrology in the Central Sierra tributaries and upper San Joaquin. Different codes will be used for each basin as there are multiple climate change simulations for each. This code is developed for the Stanislaus.


# Libraries ---------------------------------------------------------------

library(ffcAPIClient)
library(tidyverse)

# Load data ---------------------------------------------------------------

#comid and gage id to run functional flow calculator
Ann_token <- "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM"

stan_comid <- 348435
stan_gage_id <- 11299200

#climate change hydrology, with gcm indicated as object suffix
stan_access10_mcm <- read_csv("functional_flows/climate_change/Stanislaus/ACCESS1-0_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_canesm2_mcm <- read_csv("functional_flows/climate_change/Stanislaus/CanESM2_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_ccsm4_mcm <- read_csv("functional_flows/climate_change/Stanislaus/CCSM4_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_cesm1_bgc_mcm <- read_csv("functional_flows/climate_change/Stanislaus/CESM1-BGC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_cmcc_cms_mcm <- read_csv("functional_flows/climate_change/Stanislaus/CMCC-CMS_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_cnrm_cm5_mcm <- read_csv("functional_flows/climate_change/Stanislaus/CNRM-CM5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_gfdl_cm3_mcm <- read_csv("functional_flows/climate_change/Stanislaus/GFDL-CM3_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_hadgem2_cc_mcm <- read_csv("functional_flows/climate_change/Stanislaus/HadGEM2-CC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_hadgem2_es_mcm <- read_csv("functional_flows/climate_change/Stanislaus/HadGEM2-ES_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

stan_miroc5_mcm <- read_csv("functional_flows/climate_change/Stanislaus/MIROC5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

# Unit conversion of gmc hydrology ----------------------------------------

# Climate change flow files are currently in mcm (million cubic meters per day) - need to convert to cfs to match the functional flow recommendations.

#Access1-0 gcm
stan_access10_mcm <- stan_access10_mcm %>% 
  rename("flow_mcm" = "flow")

stan_access10_mcm$flow_cfs <- stan_access10_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_access10_cfs <- stan_access10_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_access10_cfs$date <- as.character(stan_access10_cfs$date)

#CanESM2 gcm
stan_canesm2_mcm <- stan_canesm2_mcm %>% 
  rename("flow_mcm" = "flow")

stan_canesm2_mcm$flow_cfs <- stan_canesm2_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_canesm2_cfs <- stan_canesm2_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_canesm2_cfs$date <- as.character(stan_canesm2_cfs$date)

#CCSM4 gcm
stan_ccsm4_mcm <- stan_ccsm4_mcm %>% 
  rename("flow_mcm" = "flow")

stan_ccsm4_mcm$flow_cfs <- stan_ccsm4_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_ccsm4_cfs <- stan_ccsm4_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_ccsm4_cfs$date <- as.character(stan_ccsm4_cfs$date)

#CESM1-BGC gcm
stan_cesm1_bgc_mcm <- stan_cesm1_bgc_mcm %>% 
  rename("flow_mcm" = "flow")

stan_cesm1_bgc_mcm$flow_cfs <- stan_cesm1_bgc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_cesm1_bgc_cfs <- stan_cesm1_bgc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_cesm1_bgc_cfs$date <- as.character(stan_cesm1_bgc_cfs$date)

#CMCC-CMS gcm
stan_cmcc_cms_mcm <- stan_cmcc_cms_mcm %>% 
  rename("flow_mcm" = "flow")

stan_cmcc_cms_mcm$flow_cfs <- stan_cmcc_cms_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_cmcc_cms_cfs <- stan_cmcc_cms_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_cmcc_cms_cfs$date <- as.character(stan_cmcc_cms_cfs$date)

#CNRM-CM5 gcm
stan_cnrm_cm5_mcm <- stan_cnrm_cm5_mcm %>% 
  rename("flow_mcm" = "flow")

stan_cnrm_cm5_mcm$flow_cfs <- stan_cnrm_cm5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_cnrm_cm5_cfs <- stan_cnrm_cm5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_cnrm_cm5_cfs$date <- as.character(stan_cnrm_cm5_cfs$date)

#GFDL-CM3 gcm
stan_gfdl_cm3_mcm <- stan_gfdl_cm3_mcm %>% 
  rename("flow_mcm" = "flow")

stan_gfdl_cm3_mcm$flow_cfs <- stan_gfdl_cm3_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_gfdl_cm3_cfs <- stan_gfdl_cm3_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_gfdl_cm3_cfs$date <- as.character(stan_gfdl_cm3_cfs$date)

#HadGEM2-CC gcm
stan_hadgem2_cc_mcm <- stan_hadgem2_cc_mcm %>% 
  rename("flow_mcm" = "flow")

stan_hadgem2_cc_mcm$flow_cfs <- stan_hadgem2_cc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_hadgem2_cc_cfs <- stan_hadgem2_cc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_hadgem2_cc_cfs$date <- as.character(stan_hadgem2_cc_cfs$date)

#HadGEM2-ES gcm
stan_hadgem2_es_mcm <- stan_hadgem2_es_mcm %>% 
  rename("flow_mcm" = "flow")

stan_hadgem2_es_mcm$flow_cfs <- stan_hadgem2_es_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_hadgem2_es_cfs <- stan_hadgem2_es_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_hadgem2_es_cfs$date <- as.character(stan_hadgem2_es_cfs$date)

#MIROC5 gcm
stan_miroc5_mcm <- stan_miroc5_mcm %>% 
  rename("flow_mcm" = "flow")

stan_miroc5_mcm$flow_cfs <- stan_miroc5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

stan_miroc5_cfs <- stan_miroc5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

stan_miroc5_cfs$date <- as.character(stan_miroc5_cfs$date)

# Observed functional flows ------------------------------------------------

ffc <- FFCProcessor$new()  # make a new object we can use to run the commands

# configure the object and run CEFF step 1 plus outputs

ffc$step_one_functional_flow_results(gage_id=stan_gage_id,
                                     token=Ann_token,
                                     output_folder = "functional_flows/Stanislaus")

# Climate change functional flows -----------------------------------------

ffc_cc <- FFCProcessor$new() #make a new object to run the functional flows for climate change hydrology

ffc_cc$flow_field <- "flow_cfs"

ffc_cc$date_format_string <- "%Y-%m-%d"

ffc_cc$timeseries_enable_filtering <- FALSE #we can do this because the filter step showed us that there were no NAs


# ACCESS1-0 functional flows ----------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_access10_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/ACCESS1-0_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()


# CanESM2 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_canesm2_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/CanESM2_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CCSM4 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_ccsm4_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/CCSM4_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CESM1-BGC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_cesm1_bgc_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/CESM1-BGC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CMCC-CMS functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_cmcc_cms_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/CMCC-CMS_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CNRM-CM5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_cnrm_cm5_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/CNRM-CM5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# GFDL-CM3 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_gfdl_cm3_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/GFDL-CM3_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()
# HadGEM2-CC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_hadgem2_cc_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/HadGEM2-CC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# HadGEM2-ES functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_hadgem2_es_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/HadGEM2-ES_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# MIROC5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = stan_miroc5_cfs, 
                                        token=Ann_token, 
                                        comid=stan_comid,
                                        output_folder = "functional_flows/climate_change/Stanislaus/MIROC5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()