

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

#Create years and bins
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

#choose vote threshold, 2, 3, or full
vote_threshold <- 3

volumes <- volumes %>%
  rename(c("industry_percentile" = sprintf("industry_%i_percentile", vote_threshold), "year_published" = "Year_rounded"))

volumes$year <- as.numeric(volumes$bin)

write.csv(volumes, "../temporary/industry_data_cleaned.csv")

#model
reference = min(bins)

mod <- feols(optimism_percentile ~ Science +
               Political.Economy +
               industry_percentile +
               Science*Political.Economy +
               Science*Religion +
               Religion*Political.Economy +
               Science*industry_percentile +
               Political.Economy*industry_percentile +
               # Religion*industry_percentile +
               Science*Political.Economy*industry_percentile +
               Science*Religion*industry_percentile +
               Religion*Political.Economy*industry_percentile +
               i(bin, Science, reference) +
               i(bin, Political.Economy, reference) +
               i(bin, industry_percentile, reference) +
               i(bin, Science*Religion, reference) +
               i(bin, Science*Political.Economy, reference) +
               i(bin, Political.Economy*Religion, reference) +
               i(bin, Science*industry_percentile, reference) +
               i(bin, Political.Economy*industry_percentile, reference) +
               # i(bin, Religion*industry_percentile, 1610) +
               i(bin, Science*Political.Economy*industry_percentile, reference) +
               i(bin, Science*Religion*industry_percentile, reference) +
               i(bin, Religion*Political.Economy*industry_percentile, reference) +
               i(bin, ref = reference) - Religion - Religion*industry_percentile + industry_percentile + year_published,
             data = volumes, cluster = c("year_published"))

# mod <- feols(optimism_percentile ~
#         i(bin, Science*Religion*industry_percentile, 1610) +
#         i(bin, Science*Political.Economy*industry_percentile, 1610) +
#         i(bin, Religion*Political.Economy*industry_percentile, 1610), data = volumes)

etable(mod)

#export to .txt file
#clustered standard errors
sink("../output/industrialization_50_year.txt")
print(summary(mod, cluster = "year_published"))
sink()

#Get results

estimates <- tibble::rownames_to_column(as.data.frame(mod$coeftable), "coefficient")


#Clean to make grouping by year and variable easier

#parse variable names into FEs and dep vars
estimates <- estimates %>%
  mutate(coefficient = str_remove(coefficient, "bin::")) %>%
  mutate(coefficient = str_replace(coefficient, '^([^0-9:]*):([^0-9:]*)$', '\\1 * \\2')) %>% #Format interactions correctly
  mutate(coefficient = str_replace(coefficient, '^([^0-9:]*):([^0-9:]*):([^0-9:]*)$', '\\1 * \\2 * \\3')) %>%
  mutate(split = strsplit(coefficient, ':')) %>%
  mutate(year = sapply(split, function(x) x[1]),
         variable = ifelse(sapply(split, length) == 2, sapply(split, function(x) x[2]), sapply(split, function(x) x[1]))) %>% #assign years and variables to correct columns
  select(-split)

#Fix some special cases
estimates <- estimates %>%
  mutate(variable = ifelse(is.na(as.numeric(variable)), variable, "(Intercept)")) %>%
  mutate(year = ifelse(is.na(as.numeric(year)), 'Reference', year)) %>%
  mutate(variable = ifelse(variable == 'Political.Economy * industry_percentile * Religion', 'Religion * Political.Economy * industry_percentile', variable)) %>%
  mutate(variable = ifelse(variable == 'Science * industry_percentile * Religion', 'Science * Religion * industry_percentile', variable))


#Reshape coefficients, std. errors, and pvalues into dfs

transform_estimates <- function(df, stat){
  transformed <- dcast(df, variable ~ year, value.var = stat)
  
  transformed <- transformed %>%
    relocate("Reference", .after = "variable") %>%
    arrange(str_length(variable), variable) %>%
    arrange(variable != "(Intercept)" & variable != "industry_percentile")
  
  return(transformed)
}
coefs <- transform_estimates(estimates, "Estimate")
std_errs <- transform_estimates(estimates, "Std. Error")
pvalue <- transform_estimates(estimates, "Pr(>|t|)")

#Get output compatible w/ modelsummary
# modelsummary_compatible <- function(split=FALSE){
#   split = FALSE
  models <- list()
  # if (split == FALSE){
  #   position = 2
  # } else {
  #   position = 10
  # }
  for (i in 2:ncol(coefs)){
    print(ncol(coefs))
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

    #10 because that is the first model in the second half of results. No way to generalize, is what it is given how we are presenting results. Change to 2 for a generalized results table.
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
# return(models)
# }

#Modelsummary table

cm <- c("Political.Economy" = "PolitEcon",
        "industry_percentile" = "Industry",
        "Science * Religion" = "$\\text{Science} \\times \\text{Religion}$",
        "Science * industry_percentile" = "$\\text{Science} \\times \\text{Industry}$",
        "Religion:industry_percentile" = "$\\text{Religion} \\times \\text{Industry}$",
        "Science * Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon}$",
        "Political.Economy * Religion" = "$\\text{Religion} \\times \\text{PolitEcon}$",
        "Science:Religion:industry_percentile" = "$\\text{Science} \\times \\text{Religion} \\times \\text{Industry}$",
        "Science:industry_percentile:Political.Economy" = "$\\text{Science} \\times \\text{PolitEcon} \\times \\text{Industry}$",
        "Religion:industry_percentile:Political.Economy" = "$\\text{Religion} \\times \\text{PolitEcon} \\times \\text{Industry}$",
        "Political.Economy * industry_percentile" = "$\\text{PolitEcon} \\times \\text{Industry}$",
        "Science * Religion * industry_percentile" = "$\\text{Science} \\times \\text{Religion} \\times \\text{Industry}$",
        "Science * Political.Economy * industry_percentile" = "$\\text{Science} \\times \\text{PolitEcon} \\times \\text{Industry}$",
        "Religion * Political.Economy * industry_percentile" = "$\\text{Religion} \\times \\text{PolitEcon} \\times \\text{Industry}$")

note <- "Volumes are placed into 20 year ((+/-) 10 year) bins. Columns represent interactions between bin fixed effects and the variables of interest (rows). Observations prior to 1600 are dropped. $Industry$ represents the industry score by percentile over the whole corpus. Standard errors are clustered by year of publication."

# models_split <- modelsummary_compatible(split = FALSE)

modelsummary(models[1:8],
             stars = TRUE,
             coef_rename = cm,
             coef_omit = "year_published",
             escape = FALSE,
             threeparttable = TRUE,
             title = "Dependent Variable: Optimism Percentile",
             output = "../output/industry_3/industry_1.tex")

modelsummary(models[9:15],
             stars = TRUE,
             coef_rename = cm,
             coef_omit = "year_published",
             escape = FALSE,
             threeparttable = TRUE,
             notes = note,
             output = "../output/industry_3/industry_2.tex")

models <- list()

for (i in 2:ncol(coefs)){
  print(ncol(coefs))
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
  
  #10 because that is the first model in the second half of results. No way to generalize, is what it is given how we are presenting results. Change to 2 for a generalized results table.
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
             coef_rename = cm,
             coef_omit = "year_published",
             escape = FALSE,
             threeparttable = TRUE,
             notes = note,
             output = "../output/industry_3/industry_combined.tex")


modelsummary(models,
             coef_omit = "year_published",
             stars = TRUE)

volumes$bin <- as.factor(volumes$bin)

bins <- as.factor(bins)


model <- lm(optimism_percentile ~ Religion * Science * industry_percentile * bin + Religion * Political.Economy * industry_percentile * bin + Science * Political.Economy * industry_percentile * bin - Religion * industry_percentile * bin + bin + bin * industry_percentile + year_published, volumes)

summary(mod)

summary(model)


bins_numeric <- as.numeric(levels(bins))

pred <- function(lm, sci, rel, pol, ind){
  cluster = vcovCL(lm, cluster = ~year_published)
  data <- data.frame(Science = sci, Political.Economy = pol, Religion = rel, industry_percentile = ind, bin = bins, year_published = bins_numeric)
  prediction <- Predict(lm, newdata = data, interval = "confidence", se.fit =TRUE, vcov = cluster)
  fit <- data.frame(prediction$fit)
  return(fit)
}

s100_0 <- pred(lm = model, sci = 1, rel = 0, pol = 0, ind = 0)
s50r50_0 <- pred(lm = model, sci = 0.5, rel = 0.5, pol = 0, ind = 0)
s50p50_0 <- pred(lm = model, sci = 0.5, rel = 0, pol = 0.5, ind = 0)
thirds_0 <- pred(lm = model, sci = 1/3, rel = 1/3, pol = 1/3, ind = 0)
r50p50_0 <- pred(lm = model, sci = 0, rel = 0.5, pol = 0.5, ind = 0)


s100_1 <- pred(lm = model, sci = 1, rel = 0, pol = 0, ind = 0.9)
s50r50_1 <- pred(lm = model, sci = 0.5, rel = 0.5, pol = 0, ind = 0.9)
s50p50_1 <- pred(lm = model, sci = 0.5, rel = 0, pol = 0.5, ind = 0.9)
thirds_1 <- pred(lm = model, sci = 1/3, rel = 1/3, pol = 1/3, ind = 0.9)
r50p50_1 <- pred(lm = model, sci = 0, rel = 0.5, pol = 0.5, ind = 0.9)

s100_0$label <- "100% Science"
s50r50_0$label <- "50% Science 50% Religion"
s50p50_0$label <- "50% Science 50% Political Economy"
thirds_0$label <- "1/3 Each"
r50p50_0$label <- "50% Religion 50% Political Economy"

s100_1$label <- "100% Science"
s50r50_1$label <- "50% Science 50% Religion"
s50p50_1$label <- "50% Science 50% Political Economy"
thirds_1$label <- "1/3 Each"
r50p50_1$label <- "50% Religion 50% Political Economy"


s100_0$bin <- bins
s50r50_0$bin <- bins
s50p50_0$bin <- bins
thirds_0$bin <- bins
r50p50_0$bin <- bins

s100_1$bin <- bins
s50r50_1$bin <- bins
s50p50_1$bin <- bins
thirds_1$bin <- bins
r50p50_1$bin <- bins

predicted_0 <- rbind(s100_0, s50r50_0, s50p50_0, thirds_0, r50p50_0)

predicted_1 <- rbind(s100_1, s50r50_1, s50p50_1, thirds_1, r50p50_1)

predicted_0$bin <- as.numeric(as.character(predicted_0$bin))
predicted_1$bin <- as.numeric(as.character(predicted_1$bin))

predicted_fig_0 <- ggplot(predicted_0, aes(x = bin, y = fit, group = label)) +
  geom_line(aes(color = label, linetype = label)) +
  geom_ribbon(aes(y = fit, ymin = lwr, ymax = upr, fill = label), alpha = 0.2) +
  labs(title = "Predicted Values (Ind = 0)", x = "Year", y = "Value") +
  ylim(-5, 45)+
  theme_light() +
  theme(legend.position = "none")

show(predicted_fig_0)


predicted_fig_1 <- ggplot(predicted_1, aes(x = bin, y = fit, group = label)) +
  geom_line(aes(color = label, linetype = label)) +
  geom_ribbon(aes(y = fit, ymin = lwr, ymax = upr, fill = label), alpha = 0.2) +
  labs(title = "Predicted Values (Ind = 90th Percentile)", x = "Year", y = "Value") +
  ylim(-5,45)+
  theme_light()

show(predicted_fig_1)

figure <- ggarrange(predicted_fig_0, predicted_fig_1,
                    labels = c("A", "B"),
                    ncol = 2, nrow =1,
                    widths = c(5.5,8))
show(figure)

ggsave("../output/industry_3/predicted_values.png", width = 13.5)


#############Test


