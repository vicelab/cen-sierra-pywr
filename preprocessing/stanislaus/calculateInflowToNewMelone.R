library(lubridate)
library(dplyr)
library(reshape2)
library(hyfo)
library(ggplot2)
library(stringr)

rm(list=ls(all=TRUE)) #start with empty workspace
scen = c('Livneh','CanESM2_rcp45','CanESM2_rcp85','CNRM-CM5_rcp45','CNRM-CM5_rcp85','HadGEM2-ES_rcp45','HadGEM2-ES_rcp85','MIROC5_rcp45','MIROC5_rcp85')
d = "C:/Users/Aditya/Box Sync/VICE Lab/RESEARCH/PROJECTS/CERC-WET/Task7_San_Joaquin_Model/Pywr models/data/Stanislaus River/"
for (s in scen){
  p <- paste(d,"Scenarios/runoff/",s, sep="")
  files <- list.files(path=p, pattern="*.csv", full.names=TRUE, recursive=FALSE)
  df_t <- data.frame()
  i = 0
  for (f in files){
    print(f)
    df <- read.csv(f)
    colnames(df) <- c("Date","Flow")
    df$Date <- as.Date(ymd(df$Date))
    if (i == 0){
      df_t <- df
    }
    else{
      df_t <- merge(df_t,df, by="Date")
    }
    i = i + 1
  }
  colnames(df_t) <- c("Date","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25")
  df_t$T_flw <- df_t$"1"+df_t$"2"+df_t$"3"+df_t$"4"+df_t$"5"+df_t$"6"+df_t$"7"+df_t$"8"+df_t$"9"+df_t$"10"+df_t$"11"+df_t$"12"+df_t$"13"+df_t$"14"+df_t$"15"+df_t$"16"+df_t$"17"+df_t$"18"+df_t$"19"+df_t$"20"+df_t$"21"+df_t$"22"+df_t$"23"+df_t$"24"+df_t$"25"
  df_f <- df_t[,c("Date","T_flw")]
  print(head(df_t))
  print(head(df_f))
  write.csv(df_f,file=paste(d,"Scenarios/preprocessed/",s,"/inflow_daily_LakeMelones_mcm.csv", sep=""), row.names = FALSE)
}  