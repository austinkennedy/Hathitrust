#Import Packages
print('Importing Packages')
import pandas as pd
import pickle
from functools import reduce
import csv
import config



#Load Data
print('Loading Data')
volumes = pd.read_csv('../temporary/volumes.csv')
industry = pd.read_csv('../input/industry_scores.csv')
industry_pre_1643 = pd.read_csv('../input/industry_scores_updated.csv')
# industry_pre_1643 = pd.read_csv('../input/industry_scores_pre_1643.csv')
sentiment = pd.read_csv('../input/sentiment_scores_march23.csv')
updated_progress = pd.read_csv('../input/updated_progress_scores.csv')



metadata = pd.read_csv('../temporary/metadata.csv')


print('Cleaning Data')
#Clean industry data
industry = industry.rename(columns={'Unnamed: 0': 'HTID', '2-vote':'industry_2','3-vote':'industry_3'})

industry_pre_1643 = industry_pre_1643.rename(columns={'Industrial Scores (May 24)': 'industry_1643'})

# industry_pre_1643 = industry_pre_1643.rename(columns = {'Unnamed: 0': 'HTID', 'Industrial Scores (June 23)': 'industry_1643'})

print(industry_pre_1643.head())

industry['HTID'] = industry['HTID'].map(lambda x: x.rstrip('.txt'))#remove '.txt' at the end of each string for HTIDs

industry_pre_1643['HTID'] = industry_pre_1643['HTID'].map(lambda x: x.rstrip('.txt'))#remove '.txt' at the end of each string for HTIDs

sentiment = sentiment.rename(columns = {'Unnamed: 0': 'HTID', 'Regression': 'percent_regression', 'Pessimism': 'percent_pessimism', 'Optimism':'percent_optimistic', 'Progress': 'percent_progress_original'})

#Clean Sentiment Data
sentiment['HTID'] = sentiment['HTID'].map(lambda x: x.rstrip('.txt')) #remove '.txt' at the end of each string for HTIDs

#NEED TO CHANGE IF YOU WANT TO INCORPORATE DIFFERENT PROGRESS SCORES
sentiment['optimism_score'] = sentiment['percent_optimistic'] + sentiment['percent_progress_original'] - sentiment['percent_pessimism'] - sentiment['percent_regression']

#Clean updated progress data
updated_progress = updated_progress.rename(columns={'Unnamed: 0': 'HTID', 'Main': 'percent_progress_main', 'Secondary': 'percent_progress_secondary'})

updated_progress['HTID'] = updated_progress['HTID'].map(lambda x: x.rstrip('.txt'))

print(updated_progress.head())


#Merge Data
print('Merging Data')
dfs = [volumes, industry, industry_pre_1643, sentiment, metadata, updated_progress]

print('Volumes Dimensions:' + str(volumes.shape))
print('Sentiment Dimensions:' + str(sentiment.shape))
print('Industry Dimensions:' + str(industry.shape))
print('Updated Progress Dimensions:' + str(updated_progress.shape))
print('Updated Industry Dimensions:' + str(industry_pre_1643.shape))

volumes_scores = reduce(lambda left,right: pd.merge(left, right, on = 'HTID', how = 'inner'), dfs) #merge on volume ID

print('Merged Dimensions:' + str(volumes_scores.shape))
#export HTIDs

htids = volumes_scores[['HTID', 'Year']]
htids.to_csv('../temporary/htids.csv')


#drop NA's and duplicates
volumes_scores = volumes_scores.dropna()
volumes_scores = volumes_scores.drop_duplicates()

volumes_scores['progress_regression_original'] = volumes_scores['percent_progress_original'] - volumes_scores['percent_regression']

volumes_scores['progress_regression_main'] = volumes_scores['percent_progress_main'] - volumes_scores['percent_regression']

volumes_scores['progress_regression_secondary'] = volumes_scores['percent_progress_secondary'] - volumes_scores['percent_regression']

#Percentiles
print('Finding Percentiles')
volumes_scores['optimism_percentile'] = volumes_scores.optimism_score.rank(pct=True, method = 'min')
volumes_scores['industry_2_percentile'] = volumes_scores.industry_2.rank(pct=True, method = 'min')
volumes_scores['industry_3_percentile'] = volumes_scores.industry_3.rank(pct=True, method = 'min')
# volumes_scores['industry_percentile'] = volumes_scores.industry.rank(pct=True, method = 'min')
volumes_scores['industry_1643_percentile'] = volumes_scores.industry_1643.rank(pct = True, method = 'min')
volumes_scores['optimistic_percentile'] = volumes_scores.percent_optimistic.rank(pct=True, method = 'min')
volumes_scores['progress_percentile_original'] = volumes_scores.percent_progress_original.rank(pct=True, method = 'min')
volumes_scores['progress_percentile_main'] = volumes_scores.percent_progress_main.rank(pct=True, method = 'min')
volumes_scores['progress_percentile_secondary'] = volumes_scores.percent_progress_secondary.rank(pct=True, method = 'min')
volumes_scores['pessimism_percentile'] = volumes_scores.percent_pessimism.rank(pct=True, method = 'min')
volumes_scores['regression_percentile'] = volumes_scores.percent_regression.rank(pct=True, method = 'min')
volumes_scores['progress_regression_percentile_original'] = volumes_scores.progress_regression_original.rank(pct=True, method = 'min')
volumes_scores['progress_regression_percentile_main'] = volumes_scores.progress_regression_main.rank(pct=True, method = 'min')
volumes_scores['progress_regression_percentile_secondary'] = volumes_scores.progress_regression_secondary.rank(pct=True, method = 'min')

print(volumes_scores['progress_percentile_main'].describe())

#Export Data
print('Exporting Data')
print(volumes_scores.head())
print(volumes_scores.columns)
print('volumes_scores Dimensions:' + str(volumes_scores.shape))
volumes_scores.to_csv('../temporary/volumes_scores.csv', index=False)

print('Creating config file for r')

with open('rconfig.csv', 'w', newline='') as csvfile:
    fieldnames = ['variable', 'value']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'variable': 'output_folder', 'value': config.output_folder})

    if config.half_century is True:
        writer.writerow({'variable': 'half_century',  'value': 'TRUE'})
    else:
        writer.writerow({'variable': 'half_century', 'value': 'FALSE'})