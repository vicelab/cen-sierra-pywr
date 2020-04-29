# Title     : TODO
# Objective : TODO
# Created by: david
# Created on: 2020-04-27

library(reshape2)
library(ggplot2)

reservoirs <- c('Lake McClure', 'Don Pedro Reservoir')
basins <- c('merced')

results_dir <- "../../results/development"

variables <- c('Reservoir_Storage_mcm')

for (var in variables) {
  for (basin in basins) {
    basin_path <-
      paste(results_dir, basin, 'historical/Livneh', sep = '/')
    variable_path <-
      paste(basin_path, paste(var, '.csv', sep = ''), sep = '/')
    
    header <-
      scan(variable_path,
           nlines = 1,
           what = character(),
           sep = ',')
    
    df <- read.csv(variable_path, skip = 3, header = F)
    names(df) <- c(c("date"), header[c(-1)])
    # rownames(df) <- df$date
    print(head(df))
    df2 <- melt(df, id.vars="date")
    
    p <- ggplot(data=df2, aes(x="date", y="value", group="variable"))
    p
  }
}