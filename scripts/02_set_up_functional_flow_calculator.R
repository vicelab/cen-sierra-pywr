
# Code overview -----------------------------------------------------------

# This code uses the functional flow package hosted on github.com/ceff-tech/ffc_api_client to assess the functional flow patterns of climate changed hydrology at the four rim dams in the San Joaquin. Separate codes will be developed for each dam. This one starts with the Tuolumne.

# Token value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM


# Libraries ---------------------------------------------------------------

library(ffcAPIClient)
library(tidyverse)


# CEFF set-up steps -------------------------------------------------------

# These initial steps are per instructions in the CEFF repository.

# Step 1

ffc <- FFCProcessor$new()  # make a new object we can use to run the commands

# configure the object and run CEFF step 1 plus outputs

ffc$step_one_functional_flow_results(gage_id=11336000,
                                     token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJBbm4iLCJsYXN0TmFtZSI6IldpbGxpcyIsImVtYWlsIjoiYXdpbGxpc0B1Y2RhdmlzLmVkdSIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNjA1NjUxMTc4fQ.MzMJ23D6tRmOD9Sr3OcQoCVLLndsV2w5ZKdzwgDOeOM",
                                     output_folder = "C:/Users/fissekis/Downloads/test")

# If using a time series csv (like model output for climate change hydrology), you can run:

#ffcAPIClient::evaluate_alteration(timeseries_df = your_df, token = "your_token", plot_output_folder = "C:/Users/youruser/Documents/Timeseries_Alteration", comid=yoursegmentcomid)

# it also *REQUIRES* you provide either a comid argument with the stream segment COMID, or both
# longitude and latitude arguments.
# If your dates are in a different format, provide the format string as argument date_format_string

# Step 2

ffc$step_two_explore_ecological_flow_criteria()
ffc$predicted_percentiles

# Step 3

ffc$step_three_assess_alteration()


# Everything works! We can now use the calculator to assess functional flows for climate change hydrology in the Central/Southern Sierra tributaries and Upper San Joaquin.
