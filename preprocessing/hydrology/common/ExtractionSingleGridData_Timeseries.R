##This script was written by Vicky Espinoza
##For use by Aditya Sood for CERC-WET
#this script extracts rainfall data from a single grid point (in this case the grid cell closest to 37.9491N, 119.7739W associated with Hetch Hethcy)
#prints csv file with date and water year, month

library(raster)
library(ncdf4)
library(maptools)
library(foreign)
library(RNetCDF)
library(rgdal)
library(lubridate)

extractPrecip <- function(src, dst, lat, lon, start, end) {

  obsdata <- nc_open(src)
  print(obsdata) # check that dims are lon-lat-time
  
  # get values at location lonlat
  obsoutput <- ncvar_get(obsdata, varid = 'rainfall',
                         start= c(which.min(abs(obsdata$dim$Lon$vals - lon)), # look for closest long
                                  which.min(abs(obsdata$dim$Lat$vals - lat)),  # look for closest lat
                                  1),
                         count = c(1,1,-1)) #count '-1' means 'all values along that dimension'that dimension'
  # create dataframe
  datafinal <- data.frame(dates= obsdatadates, obs = obsoutput)
  
  # get dates
  #obsdatadates <- as.Date(obsdata$dim$Time$vals, origin = '1950-01-01')
  date.start <- start
  date.end <- end
  d <- seq(as.Date(date.start), as.Date(date.end),1)
  datafinal$dates <- d
  datafinal$month <- month(d)
  datafinal$year <- year(d)
  datafinal$day <- day(d)
  datafinal$WY <- datafinal$year + (datafinal$month %in% 10:12) #this method is called vectorization 
  
  write.csv(datafinal, outpath)
  
  return()

}

# ====================
# Example for Tuolumne
# ====================

#climate <- "Livneh"
climate <- "MIROC5"
rcp <- 85
code <- 'DPR_I'
basin <- "TUOR"
lon <- 37.9491  # longitude of location
lat <- -119.7739 # latitude  of location

rootPath = Sys.getenv("SIERRA_DATA_PATH")

# source dir
if (climate == "Livneh") {
  start <- '1950-01-01'
  end <- '2099-12-31'
} else {
  start <- '2006-01-01'
  end <- '2099-12-31'
  rcpdir <- paste("rcp", rcp, sep="")
  srcpath <- paste(rootPath, "../precipitation", climate, rcpdir, sep="/")
  filename <- paste(climate, ".rcp", rcp, ".", code, ".LK_MC.1950-2100.monthly.BC.nc", sep="")
}
src <- paste(srcpath, filename, sep="/")

# destination path
dstdir <- paste(rootPath, "Tuolumne River", "scenarios", climate, "precipitation", sep="/")
filename <- "rainfall_Hetch_Hetchy_mcm.csv"
dst <- paste(dstdir, filename, sep="/")

extractPrecip(src, dst, lat, lon, start, end)

