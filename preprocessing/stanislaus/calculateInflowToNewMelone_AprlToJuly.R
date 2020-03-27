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
  df <- read.csv(paste(d,"scenarios/preprocessed/",s,'/inflow_daily_LakeMelones_mcm.csv', sep = ''))
  df$Date <- as.Date(ymd(df$Date))
  df$Year <- year(df$Date)
  df$Month <- month(df$Date)
  print(head(df))
  df_TF <- df %>% group_by(Year) %>% filter(Month %in% c(4,5,6,7))
  df_TF2 <- aggregate(df_TF[,2],by=list(df_TF$Year),FUN=sum,na.rm=TRUE)
  colnames(df_TF2) <- c("Year","Flow")
  df_TF2$Flow <- df_TF2$Flow*810.713 
  print(head(df_TF2))
  write.csv(df_TF2,file=paste(d,"scenarios/preprocessed/",s,"/inflow_NewMelones_AprToJul_AF.csv", sep=""), row.names = FALSE)
}