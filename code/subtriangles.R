#Libraries
library(tidyverse)
library(ggtern)
library(ggpubr)
library(patchwork)

volumes <- read.csv('../temporary/volumes_scores.csv')
half_century <- TRUE

if (half_century == TRUE){
  years <- seq(1550, 1850, by = 50)
}else{
  years <- seq(1510, 1890, by = 1)
}

#Find max and min scores for optimism and volume count
percentiles <- list()
counts <- list()

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  tmp_fig <- ggtern(df, aes(x = df$Political.Economy, y = df$Religion, z = df$Science)) + 
    geom_tri_tern(bins=5, aes(fill = ..stat.., value = df$progress_percentile), fun = mean) +
    stat_tri_tern(bins = 5, fun = mean, geom = 'point',
                  aes(size = ..count.., value = df$progress_percentile),
                  color="white",
                  centroid = TRUE) +
    labs(x = 'Political Economy', y = 'Religion', z = 'Science', title = year, fill = 'Progress (Percentile)', size = 'Volumes')
  dat <- layer_data(p, 1)
  perc <- dat$stat #grab vector of stats corresponding to triangle colors
  num <- dat$count #grab vector of column counts
  
  append(percentiles, perc)
  append(counts, num)
  
  
  
}

#Generate figures for paper

