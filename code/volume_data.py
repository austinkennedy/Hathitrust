#Import Packages
print('Importing Packages')
import pandas as pd
import pickle
from functools import reduce



#Load Data
print('Loading Data')
volumes = pd.read_csv('../temporary/volumes.csv')
industry = pd.read_csv('../input/industry_scores.csv')
sentiment = pd.read_csv('../input/sentiment_scores_march23.csv')
updated_progress = pd.read_csv('../input/updated_progress_scores.csv')
print(updated_progress.head())



#volume metadata
metadata = pickle.load(open('../input/metadata.p', 'rb'))

metadata['Year'] = pd.to_numeric(metadata['Year'], downcast='signed')

def fix_htid(row):
    return row['HTID'].replace(":","+").replace("/", "=")

metadata['HTID'] = metadata.apply(fix_htid, axis=1)
metadata.drop(columns=['oclc'], inplace=True)


print('Cleaning Data')
#Clean industry data
industry = industry.rename(columns={'Unnamed: 0': 'HTID', '2-vote':'industry_2','3-vote':'industry_3'})
industry['HTID'] = industry['HTID'].map(lambda x: x.rstrip('.txt'))#remove '.txt' at the end of each string for HTIDs

sentiment = sentiment.rename(columns = {'Unnamed: 0': 'HTID', 'Regression': 'percent_regression', 'Pessimism': 'percent_pessimism', 'Optimism':'percent_optimistic', 'Progress': 'percent_progress_original'})

#Clean Sentiment Data
sentiment['HTID'] = sentiment['HTID'].map(lambda x: x.rstrip('.txt')) #remove '.txt' at the end of each string for HTIDs


sentiment['optimism_score'] = sentiment['percent_optimistic'] + sentiment['percent_progress_original'] - sentiment['percent_pessimism'] - sentiment['percent_regression']

sentiment['progress_regression'] = sentiment['percent_progress_original'] - sentiment['percent_regression']

#Clean updated progress data
updated_progress = updated_progress.rename(columns={'Unnamed: 0': 'HTID', 'Main': 'percent_progress_main', 'Secondary': 'percent_progress_secondary'})

updated_progress['HTID'] = updated_progress['HTID'].map(lambda x: x.rstrip('.txt'))

print(updated_progress.head())


#Merge Data
print('Merging Data')
dfs = [volumes, industry, sentiment, metadata, updated_progress]

print('Volumes Dimensions:' + str(volumes.shape))
print('Sentiment Dimensions:' + str(sentiment.shape))
print('Industry Dimensions:' + str(industry.shape))
print('Updated Progress Dimensions:' + str(updated_progress.shape))

volumes_scores = reduce(lambda left,right: pd.merge(left, right, on = 'HTID', how = 'inner'), dfs) #merge on volume ID

print('Merged Dimensions:' + str(volumes_scores.shape))
#export HTIDs

htids = volumes_scores[['HTID', 'Year']]
htids.to_csv('../temporary/htids.csv')


#drop NA's and duplicates
volumes_scores = volumes_scores.dropna()
volumes_scores = volumes_scores.drop_duplicates()

#Percentiles
print('Finding Percentiles')
volumes_scores['optimism_percentile'] = volumes_scores.optimism_score.rank(pct=True)
volumes_scores['industry_2_percentile'] = volumes_scores.industry_2.rank(pct=True)
volumes_scores['industry_3_percentile'] = volumes_scores.industry_3.rank(pct=True)
volumes_scores['optimistic_percentile'] = volumes_scores.percent_optimistic.rank(pct=True)
volumes_scores['progress_percentile_original'] = volumes_scores.percent_progress_original.rank(pct=True)
volumes_scores['pessimism_percentile'] = volumes_scores.percent_pessimism.rank(pct=True)
volumes_scores['regression_percentile'] = volumes_scores.percent_regression.rank(pct=True)
volumes_scores['progress_regression_percentile'] = volumes_scores.progress_regression.rank(pct=True)
volumes_scores['progress_percentile_main'] = volumes_scores.percent_progress_main.rank(pct=True)
volumes_scores['progress_percentile_secondary'] = volumes_scores.percent_progress_secondary.rank(pct=True)


#Export Data
print('Exporting Data')
print(volumes_scores.head())
print('volumes_scores Dimensions:' + str(volumes_scores.shape))
volumes_scores.to_csv('../temporary/volumes_scores.csv', index=False)