

#clear memory and setup
rm(list=ls())
options(scipen=999)

#packages
library(tidyverse)
library(fixest)
library(data.table)
library(broom)
library(modelsummary)
library(msm)
library(ggpubr)
library(reshape2)
library(kableExtra)
library(margins)
library(sandwich)
library(car)

#load data

volumes <- read.csv('../temporary/volumes_opt_industry_all.csv')

volumes <- volumes[,-1] #Drops 'X' which is just the index attached by Python

years <- seq(1510,1890, by=1)
interval <- 50
bins <- seq(1600 + (interval/2), 1900 - (interval/2), by = interval)


# volumes <- volumes[volumes$Year_rounded >= (min(bins) - 10),]
#Merge volume years to closest bin
a = data.table(Value=volumes$Year_rounded) #Extract years
a[,merge:=Value] #Give data.table something to merge on
b = data.table(Value = bins)
b[,merge:=Value]
setkeyv(a, c('merge')) #Sort for quicker merge
setkeyv(b, c('merge'))
rounded = b[a, roll='nearest'] #Merge to nearest
rounded <- distinct(rounded) #Get distinct values for easier merge to 'volumes'
# volumes <- data.table(volumes)
volumes <- merge(volumes, rounded, by.x = "Year_rounded", by.y = "merge")
#Remove unnecessary column
volumes <- volumes %>%
  subset(select = -c(i.Value)) %>%
  rename(bin = Value)


#drop obs before 1610 bin
volumes <- volumes %>%
  filter(Year_rounded >= 1600)


volumes <- volumes %>%
  rename(c("year_published" = "Year_rounded"))

volumes$year <- as.numeric(volumes$bin)


#Regressions
reference = min(bins)

mod <- feols(optimism_percentile ~ Science 
             + Political.Economy 
             + Science*Political.Economy 
             + Science*Religion 
             + Religion*Political.Economy 
             + i(bin, Science, reference) 
             + i(bin, Political.Economy, reference) 
             + i(bin, Science*Religion, reference) 
             + i(bin, Science*Political.Economy, reference) 
             + i(bin, Political.Economy*Religion, reference) 
             + i(bin, ref = reference) - Religion + year_published, data = volumes, cluster = c("year_published"))

summary(mod)


#model with bin FE entering alone
# mod_no_interactions <- feols(optimism_percentile ~ Science + Political.Economy + Science*Political.Economy + Science*Religion + Religion*Political.Economy + i(bin, ref = 1610) - Religion, data = volumes_1)

# 
# 
# etable(mod_no_interactions)

#Group results by year and variable
estimates <- tibble::rownames_to_column(as.data.frame(mod$coeftable), "coefficient")

#add deltamethod variables

estimates <- estimates %>%
  mutate(ref = paste0("x", 1:length(estimates$coefficient)))

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
refs <- transform_estimates(estimates, "ref")



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
  if (i == 10) {
    
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
            "Science * Religion" = "$\\text{Science} \\times \\text{Religion}$", "Science:industry_percentile" = "$\\text{Science} \\times \\text{Industry}$", "Religion:industry_percentile" = "$\\text{Religion} \\times \\text{Industry}$", "Science * Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon}$", "Political.Economy * Religion" = "$\\text{Religion} \\times \\text{PolitEcon}$", "Science:Religion:industry_percentile" = "$\\text{Science} \\times \\text{Religion} \\times \\text{Industry}$", "Science:industry_percentile:Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon} \\times \\text{Industry}$", "Religion:industry_percentile:Political.Economy" = "$\\text{Religion} \\times \\text{PolitEcon} \\times \\text{Industry}$")

note <- "Volumes are placed into 20 year ((+/-) 10 year) bins. Columns represent interactions between bin fixed effects and the variables of interest (rows). Observations prior to 1600 are dropped. Standard errors are clustered by year of publication."

coef_omitted <- "year_published"

modelsummary(models, stars = TRUE)

modelsummary(models[1:8],
             stars = TRUE,
             coef_rename = rename,
             coef_omit = coef_omitted,
             title = "Dependent Variable: Optimism Percentile",
             escape = FALSE,
             threeparttable=TRUE,
             output="../output/optimism_1.tex"
)

#split into two to fit onto page

modelsummary(models[9:15],
             stars = TRUE,
             coef_rename = rename,
             coef_omit = coef_omitted,
             title = "Dependent Variable: Optimism Percentile",
             escape = FALSE,
             threeparttable = TRUE,
             notes = note,
             output="../output/optimism_2.tex"
)

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

modelsummary(models,
             stars = TRUE,
             coef_rename = rename,
             coef_omit = coef_omitted,
             title = "Dependent Variable: Optimism Percentile",
             escape = FALSE,
             threeparttable = TRUE,
             notes = note,
             output="../output/optimism_combined.tex"
)


#Marginal effects

volumes$bin <- as.factor(volumes$bin)

bins <- as_factor(bins)

model <- lm(optimism_percentile ~ Religion * Science * bin + Religion * Political.Economy * bin + Science * Political.Economy * bin - Religion - Religion * bin + Political.Economy + bin + year_published, volumes)

summary(model)

summary(mod)

#function for getting marginal effects
get_marginal_science <- function(model, s, r, p){
  cluster = vcovCL(model, cluster = ~year_published)
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

ggsave("../output/marginal_effects.png", width = 5.5)

# #Predicted Values
# library(miceadds)
# model_clustered <- lm.cluster(optimism_percentile ~ Religion * Science * bin + Religion * Political.Economy * bin + Science * Political.Economy * bin - Religion - Religion * bin + Political.Economy + bin, data = volumes, cluster = "year_published")
# 
# summary(model_clustered)

bins_numeric <- as.numeric(levels(bins))

pred <- function(lm, sci, rel, pol){
  cluster = vcovCL(lm, cluster = ~year_published)
  data <- data.frame(Science = sci, Political.Economy = pol, Religion = rel, bin = bins, year_published = bins_numeric)
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

ggsave("../output/predicted_values.png", width = 8)

figure <- ggarrange(marginal_fig, predicted_fig,
                    labels = c("A", "B"),
                    ncol = 2, nrow =1,
                    widths = c(5.5,8))
show(figure)
ggsave("../output/marginal_predicted_combined.png", width = 13.5)




########playground

test <- as.data.frame(mod$coeftable)

library(multiwayvcov)
library(lmtest)
coeftest(model, vcov.=function(y) cluster.vcov(y, ~bin, df_correction = TRUE))

get_marginal_science <- function(model, s, r, p){
  tmp <- model %>%
    margins(
      variables = "Science",
      at = list(Science = s, Religion = r, Political.Economy = p, bin = bins)
    ) %>%
    summary()
  
  return(tmp)
}
s_50r50_iid <- get_marginal_science(model = model, s = 0.5, r = 0.5, p = 0)


s50r50_p_r <- pred(lm = model_robust, sci = 0.5, rel = 0.5, pol = 0)
