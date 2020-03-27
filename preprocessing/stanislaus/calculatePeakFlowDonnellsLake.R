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
  
  df18 <- read.csv(paste(p,'/tot_runoff_sb18.csv', sep = ''))
  df19 <- read.csv(paste(p,'/tot_runoff_sb19.csv', sep = ''))
  df20 <- read.csv(paste(p,'/tot_runoff_sb20.csv', sep = ''))
  df21 <- read.csv(paste(p,'/tot_runoff_sb21.csv', sep = ''))
  colnames(df18) <- c("Date","Flow")
  df18$Date <- as.Date(ymd(df18$Date))
  colnames(df19) <- c("Date","Flow")
  df19$Date <- as.Date(ymd(df19$Date))
  colnames(df20) <- c("Date","Flow")
  df20$Date <- as.Date(ymd(df20$Date))
  colnames(df21) <- c("Date","Flow")
  df21$Date <- as.Date(ymd(df21$Date))
  
  df_t <- data.frame()
  
  df_t <- df18
  df_t <- merge(df_t,df19,by="Date")
  df_t <- merge(df_t,df20,by="Date")
  df_t <- merge(df_t,df21,by="Date")
  print(head(df_t))
  colnames(df_t) <- c("Date","F18","F19","F20","F21")
  df_t$TotFlow <-as.numeric(df_t$F18 + df_t$F19 + df_t$F20 + df_t$F21)
  df_f <- df_t[,c('Date','TotFlow')]
  write.csv(df_f,file=paste(d,"Scenarios/preprocessed/",s,"/inflow_DonnellsRes_cms.csv",sep=""), row.names = FALSE)
  df_f$Year <- year(df_f$Date)
  df_f$Month <- month(df_f$Date)
  df_FF <- df_f %>% group_by(Year) %>% filter(Month %in% c(3,4,5)) %>% filter(TotFlow == max(TotFlow))
  print(head(df_FF))
  write.csv(df_FF,file=paste(d,"Scenarios/preprocessed/",s,"/peak_runoff_DonnellsRes_MarToMay_cms.csv", sep=""), row.names = FALSE)
}
