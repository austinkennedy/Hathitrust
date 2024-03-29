library(ggtern)
library(tidyverse)


volumes <- read.csv('../temporary/volumes_scores.csv')
famous_books = read.csv('../input/famous_books.csv')

famous_merged <- merge(volumes[,c('HTID', 'Religion', 'Science', 'Political.Economy')], famous_books, by = 'HTID')

famous_selected <- famous_merged %>%
  group_by(Title) %>%
  slice_sample(n=1)

famous_selected <- famous_selected %>%
  group_by(Category) %>%
  mutate(shape = row_number())

famous_selected <- famous_selected %>%
  group_by(Category) %>%
  mutate(shape = row_number()) %>%
  arrange(Category, Title) %>%
  ungroup()

color_map <- data.frame(Category = c('Religion', 'Political Economy', 'Science'),
                        color = c('blue', 'red', 'green4'))

famous_selected <- famous_selected %>% left_join(color_map, by = 'Category')

label = seq(0,1,by=0.2)



plot <- ggtern(famous_selected, aes(x = Political.Economy, y = Religion, z = Science, shape = Title, color = Title)) +
  geom_point(size = 2, stroke = 1.2) +
  scale_shape_manual(values = famous_selected$shape, labels = famous_selected$Title, breaks = famous_selected$Title) +
  scale_color_manual(values = famous_selected$color, labels = famous_selected$Title, breaks = famous_selected$Title) +

  limit_tern(limits=c(0,1.0),
             breaks=seq(0,1,by=0.2),
             labels=label) +
  labs(x = 'Political\nEconomy', y = 'Religion', z = 'Science')+
  theme_classic() +
  theme(tern.axis.title.R = element_text(hjust=0.6, vjust = 0.9, size = 10), tern.axis.title.L = element_text(hjust = 0.3, vjust = 0.9, size = 10),
        tern.axis.title.T = element_text(size = 10),
        legend.title = element_text(size = 10, face = 'bold'), legend.text = element_text(size = 10), legend.spacing.y = unit(0.1, 'cm')) +
  guides(color = guide_legend(byrow =TRUE, size =7),
         shape = guide_legend(byrow=TRUE, size =7))
  
  

print(plot)

path <- "../output/famous_volumes.png"

ggsave(path, plot, width = 9)


