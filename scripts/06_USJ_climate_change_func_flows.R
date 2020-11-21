
# Code description --------------------------------------------------------

# This code is used to run the functional flow calculator on climate change hydrology in the Central Sierra tributaries and upper San Joaquin. Different codes will be used for each basin as there are multiple climate change simulations for each. This code is developed for the Upper_San_Joaquin.


# Libraries ---------------------------------------------------------------

library(ffcAPIClient)
library(tidyverse)

# Load data ---------------------------------------------------------------

#comid and gage id to run functional flow calculator
Ann_token <- "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM"

usj_comid <- 19791955
usj_gage_id <- 11251000

#climate change hydrology, with gcm indicated as object suffix
usj_access10_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/ACCESS1-0_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_canesm2_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/CanESM2_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_ccsm4_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/CCSM4_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_cesm1_bgc_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/CESM1-BGC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_cmcc_cms_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/CMCC-CMS_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_cnrm_cm5_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/CNRM-CM5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_gfdl_cm3_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/GFDL-CM3_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_hadgem2_cc_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/HadGEM2-CC_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_hadgem2_es_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/HadGEM2-ES_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

usj_miroc5_mcm <- read_csv("functional_flows/climate_change/Upper_San_Joaquin/MIROC5_rcp85/preprocessed/full_natural_flow_daily_mcm.csv")

# Unit conversion of gmc hydrology ----------------------------------------

# Climate change flow files are currently in mcm (million cubic meters per day) - need to convert to cfs to match the functional flow recommendations.

#Access1-0 gcm
usj_access10_mcm <- usj_access10_mcm %>% 
  rename("flow_mcm" = "flow")

usj_access10_mcm$flow_cfs <- usj_access10_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_access10_cfs <- usj_access10_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_access10_cfs$date <- as.character(usj_access10_cfs$date)

#CanESM2 gcm
usj_canesm2_mcm <- usj_canesm2_mcm %>% 
  rename("flow_mcm" = "flow")

usj_canesm2_mcm$flow_cfs <- usj_canesm2_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_canesm2_cfs <- usj_canesm2_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_canesm2_cfs$date <- as.character(usj_canesm2_cfs$date)

#CCSM4 gcm
usj_ccsm4_mcm <- usj_ccsm4_mcm %>% 
  rename("flow_mcm" = "flow")

usj_ccsm4_mcm$flow_cfs <- usj_ccsm4_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_ccsm4_cfs <- usj_ccsm4_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_ccsm4_cfs$date <- as.character(usj_ccsm4_cfs$date)

#CESM1-BGC gcm
usj_cesm1_bgc_mcm <- usj_cesm1_bgc_mcm %>% 
  rename("flow_mcm" = "flow")

usj_cesm1_bgc_mcm$flow_cfs <- usj_cesm1_bgc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_cesm1_bgc_cfs <- usj_cesm1_bgc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_cesm1_bgc_cfs$date <- as.character(usj_cesm1_bgc_cfs$date)

#CMCC-CMS gcm
usj_cmcc_cms_mcm <- usj_cmcc_cms_mcm %>% 
  rename("flow_mcm" = "flow")

usj_cmcc_cms_mcm$flow_cfs <- usj_cmcc_cms_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_cmcc_cms_cfs <- usj_cmcc_cms_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_cmcc_cms_cfs$date <- as.character(usj_cmcc_cms_cfs$date)

#CNRM-CM5 gcm
usj_cnrm_cm5_mcm <- usj_cnrm_cm5_mcm %>% 
  rename("flow_mcm" = "flow")

usj_cnrm_cm5_mcm$flow_cfs <- usj_cnrm_cm5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_cnrm_cm5_cfs <- usj_cnrm_cm5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_cnrm_cm5_cfs$date <- as.character(usj_cnrm_cm5_cfs$date)

#GFDL-CM3 gcm
usj_gfdl_cm3_mcm <- usj_gfdl_cm3_mcm %>% 
  rename("flow_mcm" = "flow")

usj_gfdl_cm3_mcm$flow_cfs <- usj_gfdl_cm3_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_gfdl_cm3_cfs <- usj_gfdl_cm3_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_gfdl_cm3_cfs$date <- as.character(usj_gfdl_cm3_cfs$date)

#HadGEM2-CC gcm
usj_hadgem2_cc_mcm <- usj_hadgem2_cc_mcm %>% 
  rename("flow_mcm" = "flow")

usj_hadgem2_cc_mcm$flow_cfs <- usj_hadgem2_cc_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_hadgem2_cc_cfs <- usj_hadgem2_cc_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_hadgem2_cc_cfs$date <- as.character(usj_hadgem2_cc_cfs$date)

#HadGEM2-ES gcm
usj_hadgem2_es_mcm <- usj_hadgem2_es_mcm %>% 
  rename("flow_mcm" = "flow")

usj_hadgem2_es_mcm$flow_cfs <- usj_hadgem2_es_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_hadgem2_es_cfs <- usj_hadgem2_es_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_hadgem2_es_cfs$date <- as.character(usj_hadgem2_es_cfs$date)

#MIROC5 gcm
usj_miroc5_mcm <- usj_miroc5_mcm %>% 
  rename("flow_mcm" = "flow")

usj_miroc5_mcm$flow_cfs <- usj_miroc5_mcm$flow_mcm/.0864*35.315

# make new df of cfs flows, check columns for NAs

usj_miroc5_cfs <- usj_miroc5_mcm %>% 
  select(date, flow_cfs) %>% 
  filter(!is.na(flow_cfs)) %>% 
  filter(!is.na(date))

usj_miroc5_cfs$date <- as.character(usj_miroc5_cfs$date)

# Observed functional flows ------------------------------------------------

ffc <- FFCProcessor$new()  # make a new object we can use to run the commands

# configure the object and run CEFF step 1 plus outputs

ffc$step_one_functional_flow_results(gage_id=usj_gage_id,
                                     token=Ann_token,
                                     output_folder = "functional_flows/Upper_San_Joaquin")

# Climate change functional flows -----------------------------------------

ffc_cc <- FFCProcessor$new() #make a new object to run the functional flows for climate change hydrology

ffc_cc$flow_field <- "flow_cfs"

ffc_cc$date_format_string <- "%Y-%m-%d"

ffc_cc$timeseries_enable_filtering <- FALSE #we can do this because the filter step showed us that there were no NAs


# ACCESS1-0 functional flows ----------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_access10_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/ACCESS1-0_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()


# CanESM2 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_canesm2_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/CanESM2_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CCSM4 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_ccsm4_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/CCSM4_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CESM1-BGC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_cesm1_bgc_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/CESM1-BGC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CMCC-CMS functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_cmcc_cms_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/CMCC-CMS_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# CNRM-CM5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_cnrm_cm5_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/CNRM-CM5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# GFDL-CM3 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_gfdl_cm3_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/GFDL-CM3_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()
# HadGEM2-CC functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_hadgem2_cc_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/HadGEM2-CC_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# HadGEM2-ES functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_hadgem2_es_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/HadGEM2-ES_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()

# MIROC5 functional flows ------------------------------------------------

ffc_cc$step_one_functional_flow_results(timeseries = usj_miroc5_cfs, 
                                        token=Ann_token, 
                                        comid=usj_comid,
                                        output_folder = "functional_flows/climate_change/Upper_San_Joaquin/MIROC5_rcp85/functional_flow_analysis/")

ffc_cc$step_two_explore_ecological_flow_criteria()

ffc_cc$step_three_assess_alteration()