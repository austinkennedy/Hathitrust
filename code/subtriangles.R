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

#Find max and min scores for optimism and volume count out of subtriangles, for use in scaling legends
percentiles <- c()
counts <- c()

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  tmp_fig <- ggtern(df, aes(x = Political.Economy, y = Religion, z = Science)) + 
    geom_tri_tern(bins=5, aes(fill = ..stat.., value = progress_percentile), fun = mean) +
    stat_tri_tern(bins = 5, fun = mean, geom = 'point',
                  aes(size = ..count.., value = progress_percentile),
                  color="white",
                  centroid = TRUE) +
    labs(x = 'Political Economy', y = 'Religion', z = 'Science', title = year, fill = 'Progress (Percentile)', size = 'Volumes')
  dat <- layer_data(tmp_fig, 1)

  percentiles <- append(percentiles, dat$stat) #append percentiles of subtriangles to list
  counts <- append(counts, dat$count) #append volume counts of subtriangles to list
  
  
  
}

#Generate figures for paper

figure_list <- list()
label = seq(0,1,by=0.2)

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  plot <- ggtern(df, aes(x = Political.Economy, y = Religion, z = Science)) +
    geom_tri_tern(bins=5, aes(fill=..stat.., value = progress_percentile), fun = mean) +
    stat_tri_tern(bins = 5, fun = mean, geom='point',
                  aes(size=..count.., progress_percentile),
                  color='white', centroid = TRUE) +
    labs(x = 'Political\nEconomy', y = "Religion", z = "Science", title = year, fill = 'Progress (Percentile)', size = "Volumes") +
    
    #  scale_fill_gradient(low="blue", high="red", na.value="white") +    #Uncomment for red/blue theme
    # scale_fill_gradient(low="blue", high="red", na.value="white", limits = c(0,1)) + #Uncomment for red/blue theme with full gradient scale
    # scale_fill_gradient(low="#56B1F7",high="#132B43", na.value="white",limits=c(0,1))+ #Uncomment for blue theme with full percentile gradient scale
    # scale_fill_gradient(low = "#56B1F7",high="#132B43", na.value="white")+#Uncomment for blue theme    
    

    scale_fill_gradient(low = "#56c7f7",high="#132B43", na.value="white",
                        limits = c(min(percentiles), max(percentiles)))+#Lighter blue
    scale_size_continuous(range = c(0,10),
                          limits = c(min(counts), max(counts)),
                          breaks = c(10, 100, 1000, 2500, 5000, 8000, 12500)) + #Set limits and breaks of volume dots
    scale_T_continuous(limits=c(0,1.0),
                       breaks=seq(0,1,by=0.2),
                       labels=label) +
    scale_L_continuous(limits=c(0.0,1),
                       breaks=seq(0,1,by=0.2),
                       labels=label) +
    scale_R_continuous(limits=c(0.0,1),
                       breaks=seq(0,1,by=0.2),
                       labels=label)+
    theme_dark()+
    guides(size= guide_legend(reverse=TRUE, order = 0))+
    theme(tern.axis.title.R = element_text(hjust=0.6))
  
  show(plot)
  # tmp <- ggplotGrob(plot)

  figure_list[[toString(year)]] <- plot
}

fig <- wrap_plots(figure_list, ncol = 2, nrow = 4) + plot_layout(widths = c(1,15,5), guides = "collect") & theme(legend.position = "right")

ggplot2::ggsave('../output/subtriangles/heat_fig.png', fig)

show(print(fig))

ggtern::grid.arrange(grobs = figure_list, ncol=2, nrow=4)



















