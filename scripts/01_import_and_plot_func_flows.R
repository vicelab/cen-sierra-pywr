
# Code description --------------------------------------------------------

# This code is used to import the functional flow metrics developed by Yarnell et al. (2020) and apply them to the rim dams in the four study basins: Stanislaus, Tuolumne, Merced, and San Joaquin. First, the code will be developed for the Merced because it has the simplest network; then it can be adapted for the other study basins.


# Libraries ---------------------------------------------------------------

library(tidyverse)
library(plotly)
library(lubridate)
library(lfstat)

# Load data ---------------------------------------------------------------

options(scipen = 999)

all_basins_func_flows <- read_csv("functional_flows/TNC_ffm_2823750tuol_348435stan_21607271mer_19791955sj.csv")

#Stanislaus, Tuolumne, and San Joaquin units are mcm (million cubic meters per day). Merced units are cfs (cubic feet per second)
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

# Unimpaired flow files for Tuolumne, Stanislaus, and San Joaquin are currently in mcm (million cubic meters per day) - need to convert to cfs to match the functional flow recommendations.

#Rename columns for clarity
Stanislaus_unimpaired_flow <- Stanislaus_unimpaired_flow %>% 
  rename("flow_mcm" = "flow")

Stanislaus_unimpaired_flow$flow_cfs <- Stanislaus_unimpaired_flow$flow_mcm/.0864*35.315

ggplotly(
  ggplot() +
    geom_line(data = Stanislaus_unimpaired_flow, aes(x=date, y=flow_cfs), color = "darkblue") +
    labs(title = "Stanislaus", x = "Date", y = "Unimpaired flow (cfs)")
)


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

# filter to focus on moderate season metrics

Merced_func_flow_moderate <- Merced_func_flow %>% 
  filter(wyt == "moderate")

# I learned that the flow schedule for the Tuolumne is already developed. I'm reproducing it here and will make plots using this site.

# Plot Tuolumne flows -----------------------------------------------------

#Rename columns for clarity

Tuolumne_unimpaired_flow <- Tuolumne_unimpaired_flow %>% 
  rename("flow_mcm" = "flow") 

#Convert flow_cmc to flow_cfs
Tuolumne_unimpaired_flow$flow_cfs <- Tuolumne_unimpaired_flow$flow_mcm/.0864*35.315

#Add 40% unimpaired flow as per SWRCB policy
Tuolumne_unimpaired_flow$FNF_40_percent <- Tuolumne_unimpaired_flow$flow_cfs*0.4

#Plot to view initial results
ggplotly(
  ggplot() +
    geom_line(data = Tuolumne_unimpaired_flow, aes(x=date, y=flow_cfs), color = "darkblue") +
    geom_line(data = Tuolumne_unimpaired_flow, aes(x=date, y=FNF_40_percent), color = "sienna3") +
    labs(title = "Tuolumne River", x = "Date", y = "Flow (cfs)")
)

#Filter functional flow recommendations to build flow schedules
Tuolumne_func_flow_moderate <- Tuolumne_func_flow %>% 
  filter(wyt == "moderate")

#Build moderate season functional flow schedule
T_FFM_mod <- c("dry season baseflow", NA, "fall pulse", NA, NA, NA, "low wet baseflow", "median wet baseflow", NA, "spring recession start", "ramp down", "dry season baseflow", NA)

T_DOWY_mod <- c(1, 18, 19, 20, 21, 22, 123, 125, 239, 240, 270, 305, 365)
T_mag_cfs_mod <- c(155, 155, 1182, 1182, 1182, 155, 1175, 3625, 3625, 16450, 2005, 155, 155)

Tuolumne_func_flow_schedule_moderate <- data.frame(T_FFM_mod, T_DOWY_mod, T_mag_cfs_mod)

#build dry season functional flow schedule
T_FFM_dry <- c("dry season baseflow", NA, "fall pulse", NA, NA, NA, "low wet baseflow", "median wet baseflow", NA, "spring recession start", "ramp down", "dry season baseflow", NA)

T_DOWY_dry <- c(1, 9, 10, 11, 12, 13, 119, 121, 222, 223, 243, 278, 365)
T_mag_cfs_dry <- c(105, 105, 560, 560, 105, 105, 192, 1528, 1528, 6346, 1598, 105, 105)

Tuolumne_func_flow_schedule_dry <- data.frame(T_FFM_dry, T_DOWY_dry, T_mag_cfs_dry)

#Test plot functional flow schedule

ggplot()+
  geom_line(data = Tuolumne_func_flow_schedule_dry, aes(x=T_DOWY_dry, y=T_mag_cfs_dry))

#Select dry season period, add julian date, and plot with functional flow schedule

Tuolumne_unimpaired_flow <- Tuolumne_unimpaired_flow %>% 
  mutate(julian_day=yday(date))

Tuolumne_unimpaired_flow <- Tuolumne_unimpaired_flow %>% 
  mutate(water_day = if_else(julian_day > 273, julian_day-273, julian_day+(365-273)), 
         water_year = as.numeric(as.character(water_year(date, "usgs"))))


# Tuolumne: WY1976 --------------------------------------------------------

Tuolumne_unimpaired_flow_1976 <- Tuolumne_unimpaired_flow %>% 
  filter(water_year == "1976")

#join data so that functional flow schedule is in Tuolumne_unimpaired flow data frame

#rename column in FF schedule for join:
Tuolumne_func_flow_schedule_dry  <-  Tuolumne_func_flow_schedule_dry %>% 
  rename("julian_day" = "T_DOWY_dry")

Tuolumne_all_flows_1976 <- left_join(Tuolumne_unimpaired_flow_1976, Tuolumne_func_flow_schedule_dry, by="julian_day")

ggplotly(
  ggplot() +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=julian_day, y=flow_cfs), color = "darkblue") +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=julian_day, y=FNF_40_percent), color = "sienna3") +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=julian_day, y=T_mag_cfs_dry), color = "springgreen3") +
    labs(title = "Tuolumne River", x = "Date", y = "Flow (cfs)")
)

#Ugh. Need to fill in functional flows for each row to get a continuous plot.

Tuolumne_all_flows_1976[1:9,9] <- 105
Tuolumne_all_flows_1976[10:11,9] <- 560
Tuolumne_all_flows_1976[12:118,9] <- 105
Tuolumne_all_flows_1976[119,9] <- 192
Tuolumne_all_flows_1976[120,9] <- 860
Tuolumne_all_flows_1976[121:222,9] <- 1528
Tuolumne_all_flows_1976[223,9] <- 6346

#calculate m2 and b2 for recession limb line
y2 <- 1598
x2 <- 243
m2 <- (1598-6346)/(243-223)
b2 <- y2-(m2*x2)

Tuolumne_all_flows_1976[224:242,9] <- m2*Tuolumne_all_flows_1976[224:242,6]+b2
Tuolumne_all_flows_1976[243,9] <- 1598

#caclulate m3 and b3 for ramp down to dry season baseflow
m3 <- (105-1598)/(278-243)
b3 <- 105-(m3*278)

Tuolumne_all_flows_1976[244:277,9] <- m3*Tuolumne_all_flows_1976[244:277,6]+b3
Tuolumne_all_flows_1976[278:365,9] <- 105

ggplotly(
  ggplot() +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=date, y=flow_cfs), color = "darkblue") +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=date, y=FNF_40_percent), color = "sienna3") +
    geom_line(data = Tuolumne_all_flows_1976, aes(x=date, y=T_mag_cfs_dry), color = "springgreen3") +
    labs(title = "Tuolumne River", x = "Date", y = "Flow (cfs)") +
    scale_fill_discrete(name = "flow schedule", labels = c("unimpaired", "40% unimpaired", "functional flow"))
)

ggsave("functional_flows/figures/Tuolumne_WY1976.png", dpi = 300, width = 9, height = 7, units = "in")


# Tuolumne WY 2006 --------------------------------------------------------

Tuolumne_all_flows_2006 <- Tuolumne_unimpaired_flow %>% 
  filter(water_year == "2006")

#add functional flow schedule for wet year

# Tuolumne: add functional flows for wet yeat -----------------------------


Tuolumne_all_flows_2006$T_FFM_wet <- as.character(NA)
Tuolumne_all_flows_2006$T_mag_cfs_wet <- as.numeric(NA)
Tuolumne_all_flows_2006[1:18,9] <- 210
Tuolumne_all_flows_2006[19:21,9] <- 2200
Tuolumne_all_flows_2006[22,9] <- 210

#calculate flows between dry season baseflow and low wet season baseflow
x1 <- 94
y1 <- 2590
m1 <- (210-y1)/(22-x1)
b1 <- y1-(m1*x1)

Tuolumne_all_flows_2006[23:93,9] <- m1*Tuolumne_all_flows_2006[23:93,6]+b1
Tuolumne_all_flows_2006[94,9] <- 2590
Tuolumne_all_flows_2006[95,9] <- mean(c(2590,5705))
Tuolumne_all_flows_2006[96:257,9] <- 5705
Tuolumne_all_flows_2006[258,9] <- 23720

#calculate flows for ramp down
x2_wet <- 278
y2_wet <- 4865
m2_wet <- (23720-y2_wet)/(258-x2_wet)
b2_wet <- y2_wet-(m2_wet*x2_wet)

Tuolumne_all_flows_2006[259:277,9] <- m2_wet*Tuolumne_all_flows_2006[259:277,6]+b2_wet
Tuolumne_all_flows_2006[278,9] <- 4865

#calculate flows for 2nd ramp down
x3_wet <- 300
y3_wet <- 725
m3_wet <- (4865-y3_wet)/(278-x3_wet)
b3_wet <- y3_wet-(m3_wet*x3_wet)

Tuolumne_all_flows_2006[279:299,9] <- m3_wet*Tuolumne_all_flows_2006[279:299,6]+b3_wet
Tuolumne_all_flows_2006[300,9] <- 725

# calculate flows for 3rd ramp down
x4_wet <- 318
y4_wet <- 309
m4_wet <- (x3_wet-y4_wet)/(y3_wet-x4_wet)
b4_wet <- y4_wet-(m4_wet*x4_wet)

Tuolumne_all_flows_2006[301:318,9] <- m4_wet*Tuolumne_all_flows_2006[301:318,6]+b4_wet

#calculate flows for 4th ramp down
x5_wet <- 326
y5_wet <- 210
m5_wet <- (x4_wet-y5_wet)/(y4_wet-x5_wet)
b5_wet <- y5_wet-(m5_wet*x5_wet)

Tuolumne_all_flows_2006[319:326,9] <- m5_wet*Tuolumne_all_flows_2006[319:326,6]+b5_wet
Tuolumne_all_flows_2006[267:365,9] <- 210

ggplotly(
  ggplot() +
    geom_line(data = Tuolumne_all_flows_2006, aes(x=date, y=flow_cfs), color = "darkblue") +
    geom_line(data = Tuolumne_all_flows_2006, aes(x=date, y=FNF_40_percent), color = "sienna3") +
    geom_line(data = Tuolumne_all_flows_2006, aes(x=date, y=T_mag_cfs_wet), color = "springgreen3") +
    labs(title = "Tuolumne River", x = "Date", y = "Flow (cfs)") +
    scale_fill_discrete(name = "flow schedule", labels = c("unimpaired", "40% unimpaired", "functional flow"))
)

ggsave("functional_flows/figures/Tuolumne_WY2006.png", dpi = 300, width = 9, height = 7, units = "in")

