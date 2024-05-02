#Libraries
library(tidyverse)
library(ggtern)
library(ggpubr)
library(patchwork)

volumes <- read.csv('../temporary/volumes_scores.csv')
config <- read.csv('rconfig.csv')
half_century <- as.logical(config[config$variable == 'half_century', 'value'])
output_folder <- config[config$variable == 'output_folder', 'value']

if (half_century == TRUE){
  years <- seq(1550, 1850, by = 50)
}else{
  years <- seq(1510, 1890, by = 1)
}

#Find max and min scores for optimism and volume count out of subtriangles, for use in scaling legends
percentiles <- c()
vol_count <- c()

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  tmp_fig <- ggtern(df, aes(x = Political.Economy, y = Religion, z = Science)) + 
    geom_tri_tern(bins=5, aes(fill = ..stat.., value = progress_percentile_main), fun = mean) +
    stat_tri_tern(bins = 5, geom = 'point',
                  aes(size = ..count.., value = progress_percentile_main),
                  color="white",
                  centroid = TRUE) +
    labs(x = 'Political Economy', y = 'Religion', z = 'Science', title = year, fill = 'Progress (Percentile)', size = 'Volumes')
  dat <- layer_data(tmp_fig, 1)

  percentiles <- append(percentiles, dat$stat) #append percentiles of subtriangles to list
  vol_count <- append(vol_count, dat$count) #append volume counts of subtriangles to list
  
  
  
}

percentiles <- na.omit(percentiles)
vol_count <- na.omit(vol_count)
#Generate figures for paper

figure_list <- list()
label = seq(0,1,by=0.2)

#create filepath with .gitignore
path <- paste(output_folder, 'subtriangles', sep = '')
if (!dir.exists(path)){
  dir.create(path, recursive = TRUE)
  
  #write .gitignore
  ignorepath <- file.path(path, '.gitignore')
  file <- file(ignorepath)
  content <- "*
*/
!.gitignore"
  writeLines(content, file)
  close(file)
  print('directory created')
}else{
  print('dir exists')
}

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  plot <- ggtern(df, aes(x = Political.Economy, y = Religion, z = Science)) +
    geom_tri_tern(bins=5, aes(fill=..stat.., value = progress_percentile_main), fun = mean) +
    stat_tri_tern(bins = 5, geom='point',
                  aes(size=..count.., progress_percentile_main),
                  color='white', centroid = TRUE) +
    labs(x = 'Political\nEconomy', y = "Religion", z = "Science", title = year, fill = 'Progress (Percentile)', size = "Volumes") +
    
    #  scale_fill_gradient(low="blue", high="red", na.value="white") +    #Uncomment for red/blue theme
    # scale_fill_gradient(low="blue", high="red", na.value="white", limits = c(0,1)) + #Uncomment for red/blue theme with full gradient scale
    # scale_fill_gradient(low="#56B1F7",high="#132B43", na.value="white",limits=c(0,1))+ #Uncomment for blue theme with full percentile gradient scale
    # scale_fill_gradient(low = "#56B1F7",high="#132B43", na.value="white")+#Uncomment for blue theme    
    

    scale_fill_gradient(low = "#56c7f7",high="#132B43", na.value="white",
                        limits = c(0, 1),
                        breaks = c(0,0.25, 0.5, 0.75, 1))+#Lighter blue

    scale_size_continuous(range = c(0,10),
                          limits = c(1, 8000),
                          breaks = c(10, 100, 1000, 2500, 5000, 8000)) + #Set limits and breaks of volume dots
  
    limit_tern(limits=c(0,1.0),
               breaks=seq(0,1,by=0.2),
               labels=label)+

    guides(size=guide_legend(reverse=TRUE, order = 0),
           fill = guide_colorbar(title = 'Percentile',
                                 limits = c(0,1),
                                 breaks = seq(0,1,by=0.25)))+
    theme_dark()+
    {if(year != 1850)theme(legend.position = "none")}+
    theme(tern.axis.title.R = element_text(hjust=0.6, vjust = 0.9), tern.axis.title.L = element_text(hjust = 0.3, vjust = 0.9))
  
  show(plot)
  # tmp <- ggplotGrob(plot)

  # figure_list[[toString(year)]] <- plot
  
  ggsave(paste(path, '/', year, '.png', sep = ''),width = 6.5, height = 4.5)
}

# fig <- wrap_plots(figure_list, ncol = 2, nrow = 4) + plot_layout(widths = c(1,15,5), guides = "collect") & theme(legend.position = "right")
# 
# ggplot2::ggsave(paste(path, '/heat_fig.png', sep = ''), fig)
# 
# show(print(fig))
# 
# ggtern::grid.arrange(grobs = figure_list, ncol=2, nrow=4)


for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  plot <- ggtern(df, aes(x = Political.Economy, y = Religion, z = Science, color = progress_percentile_main)) + geom_point()
  
  show(plot)
}
















