library(ggtern)
library(tidyverse)
library(biscale)
library(cowplot)


volumes <- read.csv('../temporary/volumes_scores.csv')
config <- read.csv('rconfig.csv')
half_century <- as.logical(config[config$variable == 'half_century', 'value'])
output_folder <- config[config$variable == 'output_folder', 'value']

bi_palette <- 'DkViolet2'
dimensions <- 4


if (half_century == TRUE){
  years <- seq(1550, 1850, by = 50)
}else{
  years <- seq(1510, 1890, by = 1)
}

#create filepath with .gitignore
path <- paste(output_folder, 'biscale_triangles', sep = '')
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

volumes <- bi_class(volumes, x = progress_percentile_main, y = industry_1643_percentile, style = 'equal', dim = dimensions)

for (year in years){
  df <- volumes %>% filter(Year >= year - 10,
                           Year <= year + 10)
  
  fig <- ggtern(data = df, mapping = aes(x = Political.Economy, y = Religion, z = Science ,color = bi_class)) +
    geom_point(show.legend = FALSE) +
    bi_scale_color(pal = bi_palette, dim = 4) +
    labs(x = 'Political\nEconomy', y = 'Religion', z = 'Science', title = year) +
    limit_tern(limits=c(0,1.0),
               breaks=seq(0,1,by=0.2),
               labels=seq(0,1,by=0.2))+
    theme_classic() +
    theme(tern.axis.title.R = element_text(hjust=0.6, vjust = 0.9, size = 18),
          tern.axis.title.L = element_text(hjust = 0.3, vjust = 0.9, size = 18),
          tern.axis.title.T = element_text(size = 18),
          title = element_text(size = 18),
          axis.text = element_text(size = 15),
          plot.margin = margin(0,0,-15,0))
  
  if(year == 1850){
  legend <- bi_legend(pal = bi_palette,
                      dim = dimensions,
                      xlab = "Higher Progress",
                      ylab = "Higher Industry",
                      size = 18)
  
  fig_go <- ggplotGrob(fig)
  
  fig_combined <- ggdraw() +
    draw_plot(fig_go, 0, 0, 1, 1) +
    draw_plot(legend, 0.62, 0.4, 0.5, 0.5)
  show(fig_combined)
  ggsave(paste(path, '/', year, '.png', sep = ''), plot = fig_combined, width = 12, height = 6.5)
  
  }else{
    show(fig)
    ggsave(paste(path, '/', year, '.png', sep = ''), plot = fig, width = 8, height = 6.5)
  }
}













