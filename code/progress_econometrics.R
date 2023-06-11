#clear memory and setup
rm(list=ls())
options(scipen=999)

library(tidyverse)
library(data.table)
library(modelsummary)
library(fixest)
library(sandwich)
library(margins)
library(car)
library(ggpubr)


volumes <- read.csv('../temporary/volumes_scores.csv')

#Create years and bins, set global params
years <- seq(1510, 1890, by = 1)
min_year <- 1600
interval <- 50
bins <- seq(min_year + (interval/2), 1900 - (interval/2), by = interval)

#Merge volumes to closest bin
a = data.table(Value=volumes$Year) #Extract years
a[,merge:=Value] #Give data.table something to merge on
b = data.table(Value = bins)
b[,merge:=Value]
setkeyv(a, c('merge')) #Sort for quicker merge
setkeyv(b, c('merge'))
rounded = b[a, roll = 'nearest'] #Merge to nearest bin
rounded <- distinct(rounded) #Get distinct values for easier merge to 'volumes'

volumes <- merge(volumes, rounded, by.x = "Year", by.y = "merge")
#Remove unnecessary column
volumes <- volumes %>%
  subset(select = -c(i.Value)) %>%
  rename(bin = Value)

#Drop obs before 1600

volumes <- volumes %>%
  filter(Year > min_year)

#Regressions
reference = min(bins)

econometrics <- function(progress_percentile){
  
#Uses feols to carry clustered SEs throughout
mod <- feols(.[progress_percentile] ~ Science 
             + Political.Economy 
             + Science*Political.Economy 
             + Science*Religion 
             + Religion*Political.Economy 
             + i(bin, Science, reference) 
             + i(bin, Political.Economy, reference) 
             + i(bin, Science*Religion, reference) 
             + i(bin, Science*Political.Economy, reference) 
             + i(bin, Political.Economy*Religion, reference) 
             + i(bin, ref = reference) 
             - Religion 
             + Year, data = volumes, cluster = c("Year"))

summary(mod)

estimates <- tibble::rownames_to_column(as.data.frame(mod$coeftable), "coefficient")

#parse variable names into FEs and dep vars


estimates <- estimates %>%
  mutate(coefficient = str_remove(coefficient, "bin::")) %>%
  mutate(coefficient = str_replace(coefficient, '^([^0-9:]*):([^0-9:]*)$', '\\1 * \\2')) %>% #Format interactions correctly
  mutate(split = strsplit(coefficient, ':')) %>%
  mutate(year = sapply(split, function(x) x[1]),
         variable = ifelse(sapply(split, length) == 2, sapply(split, function(x) x[2]), sapply(split, function(x) x[1]))) %>% #assign years and variables to correct columns
  select(-split)

estimates <- estimates %>%
  mutate(variable = ifelse(is.na(as.numeric(variable)), variable, "(Intercept)")) %>%
  mutate(year = ifelse(is.na(as.numeric(year)), 'Reference', year))

#Reshape coefficients and std errors into dfs

transform_estimates <- function(df, stat){
  transformed <- dcast(df, variable ~ year, value.var = stat)
  
  transformed <- transformed %>%
    relocate("Reference", .after = "variable") %>%
    arrange(str_length(variable), variable) %>%
    arrange(variable != "(Intercept)")
  
  return(transformed)
}

coefs <- transform_estimates(estimates, "Estimate")
std_errs <- transform_estimates(estimates, "Std. Error")
pvalue <- transform_estimates(estimates, "Pr(>|t|)")



#Get output into models to be compatible with modelsummary
models <- list()

for (i in 2:ncol(coefs)){
  
  model <- list()
  
  class(model) <- "custom"
  
  tidy.custom <- function(x, ...) {
    data.frame(
      term = coefs$variable,
      estimate = coefs[[i]],
      std.error = std_errs[[i]],
      p.value = pvalue[[i]]
    )
  }
  
  #10 because that is the first model in the second of the split results table. Need to change to 2 if going for one continuous table
  if (i == 2) {
    
    glance.custom <- function(x, ...) {
      data.frame(
        "nobs" = mod$nobs,
        "r.squared" = glance(mod)$r.squared
        # "adj.r.squared" = glance(mod)$adj.r.squared
      )
    }
  } else{
    glance.custom <- function(x, ...) {
      data.frame(
      )
    }
  }
  models[[colnames(coefs)[[i]]]] <- modelsummary(model, output = "modelsummary_list")
}

#r Main results table
rename <- c("Political.Economy" = "PolitEcon", "industry_percentile" = "Industry",
            "Science * Religion" = "$\\text{Science} \\times \\text{Religion}$",
            "Science:industry_percentile" = "$\\text{Science} \\times \\text{Industry}$",
            "Religion:industry_percentile" = "$\\text{Religion} \\times \\text{Industry}$",
            "Science * Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon}$",
            "Political.Economy * Religion" = "$\\text{Religion} \\times \\text{PolitEcon}$",
            "Science:Religion:industry_percentile" = "$\\text{Science} \\times \\text{Religion} \\times \\text{Industry}$",
            "Science:industry_percentile:Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon} \\times \\text{Industry}$",
            "Religion:industry_percentile:Political.Economy" = "$\\text{Religion} \\times \\text{PolitEcon} \\times \\text{Industry}$")

note <- "Volumes are placed into 50 year ((+/-) 25 year) bins. Columns represent interactions between bin fixed effects and the variables of interest (rows). Observations prior to 1600 are dropped. Standard errors are clustered by year of publication."

coef_omitted <- "Year"


modelsummary(models, stars = TRUE)


modelsummary(models,
             stars = TRUE,
             coef_rename = rename,
             coef_omit = coef_omitted,
             title = "Dependent Variable: Optimism Percentile",
             escape = FALSE,
             threeparttable = TRUE,
             notes = note,
             output="../output/regression_tables/progress/progress_results.tex"
)

#Marginal effects

volumes$bin <- as.factor(volumes$bin)#as factor for easier regression

bins <- as_factor(bins)#gives 'margins' input values

#Use lm() to be compatible with 'margins' package

model <- lm(progress_percentile ~ Religion * Science * bin + Religion * Political.Economy * bin + Science * Political.Economy * bin - Religion - Religion * bin + Political.Economy + bin + Year, volumes)

summary(model)

summary(mod)

#function for getting marginal effects
get_marginal_science <- function(model, s, r, p){
  cluster = vcovCL(model, cluster = ~Year)
  tmp <- model %>%
    margins(
      variables = "Science",
      at = list(Science = s, Religion = r, Political.Economy = p, bin = bins),
      vcov = cluster
    ) %>%
    summary()
  
  return(tmp)
}

s100_m <- get_marginal_science(model = model, s = 1, r = 0, p = 0)
s50r50_m <- get_marginal_science(model = model, s = 0.5, r = 0.5, p = 0)
s50p50_m <- get_marginal_science(model = model, s = 0.5, r = 0, p = 0.5)
thirds_m <- get_marginal_science(model = model, s = 1/3, r = 1/3, p = 1/3)
r50p50_m <- get_marginal_science(model = model, s = 0, r = 0.5, p = 0.5)

s100_m$label <- "100% Science"
s50r50_m$label <- "50% Science 50% Religion"
s50p50_m$label <- "50% Science 50% Political Economy"
thirds_m$label <- "1/3 Each"
r50p50_m$label <- "50% Religion 50% Political Economy"

s100_m$bin <- bins
s50r50_m$bin <- bins
s50p50_m$bin <- bins
thirds_m$bin <- bins
r50p50_m$bin <- bins

marg <- rbind(s100_m, s50r50_m, s50p50_m, thirds_m, r50p50_m)

#export/import since computation takes a while
write.csv(marg, "../temporary/marginal_main.csv")

marg <- read.csv("../temporary/marginal_main.csv")
# 

marg$bin <- as.numeric(as.character(marg$bin))


marginal_fig <- ggplot(marg, aes(x = bin, y = AME, group = label)) +
  geom_line(aes(color = label, linetype = label)) +
  geom_ribbon(aes(y = AME, ymin = lower, ymax = upper, fill = label), alpha = 0.2) +
  labs(title = "Marginal Effects", x = "Year", y = "Value") +
  # scale_x_discrete(breaks = c(1600, 1700, 1800, 1900)) +
  theme_light() +
  theme(legend.position = "none")

show(marginal_fig)

ggsave("../output/regression_figures/progress/marginal_effects.png", width = 5.5)

#Predicted Values
bins_numeric <- as.numeric(levels(bins))

pred <- function(lm, sci, rel, pol){
  cluster = vcovCL(lm, cluster = ~Year)
  data <- data.frame(Science = sci, Political.Economy = pol, Religion = rel, bin = bins, Year = bins_numeric)
  prediction <- Predict(lm, newdata = data, interval = "confidence", se.fit =TRUE, vcov = cluster)
  fit <- data.frame(prediction$fit)
  return(fit)
}


s100_p <- pred(lm = model, sci = 1, rel = 0, pol = 0)
s50r50_p <- pred(lm = model, sci = 0.5, rel = 0.5, pol = 0)
s50p50_p <- pred(lm = model, sci = 0.5, rel = 0, pol = 0.5)
thirds_p <- pred(lm = model, sci = 1/3, rel = 1/3, pol = 1/3)
r50p50_p <- pred(lm = model, sci = 0, rel = 0.5, pol = 0.5)

s100_p$label <- "100% Science"
s50r50_p$label <- "50% Science 50% Religion"
s50p50_p$label <- "50% Science 50% Political Economy"
thirds_p$label <- "1/3 Each"
r50p50_p$label <- "50% Religion 50% Political Economy"

s100_p$bin <- bins
s50r50_p$bin <- bins
s50p50_p$bin <- bins
thirds_p$bin <- bins
r50p50_p$bin <- bins

predicted <- rbind(s100_p, s50r50_p, s50p50_p, thirds_p, r50p50_p)

predicted$bin <- as.numeric(as.character(predicted$bin))

predicted_fig <- ggplot(predicted, aes(x = bin, y = fit, group = label)) +
  geom_line(aes(color = label, linetype = label)) +
  geom_ribbon(aes(y = fit, ymin = lwr, ymax = upr, fill = label), alpha = 0.2) +
  labs(title = "Predicted Values", x = "Year", y = "Value") +
  theme_light()

show(predicted_fig)

ggsave("../output/regression_figures/progress/predicted_values.png", width = 8)

figure <- ggarrange(marginal_fig, predicted_fig,
                    labels = c("A", "B"),
                    ncol = 2, nrow =1,
                    widths = c(5.5,8))
show(figure)
ggsave("../output/regression_figures/progress/marginal_predicted_combined.png", width = 13.5)


}

econometrics('progress_percentile_original')







