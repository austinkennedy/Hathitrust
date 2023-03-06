#Import Packages
print('Importing Packages')
import pandas as pd
import pickle
from functools import reduce

#change to 'False' if using old data
updated = True

#Load Data
print('Loading Data')
volumes = pd.read_csv('../temporary/volumes.csv')
industry = pd.read_csv('../input/industry_scores.csv')

if updated is True:
    sentiment = pd.read_csv('../input/sentiment_scores_updated.csv')
else:
    sentiment = pd.read_csv('../input/sentiment_scores.csv')

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

#Clean Sentiment Data

if updated is True:
    sentiment = sentiment.rename(columns = {'score': 'optimism_score'})
    sentiment['HTID'] = sentiment['HTID'].map(lambda x: x.rstrip('.txt'))
else:
    sentiment.drop(columns=['Unnamed: 0', 'key'], inplace=True)

    sentiment['optimism_score'] = sentiment['percent_optimistic'] + sentiment['percent_progress'] - sentiment['percent_pessimism'] - sentiment['percent_regression']


#Merge Data
print('Merging Data')
dfs = [volumes, industry, sentiment, metadata]

volumes_scores = reduce(lambda left,right: pd.merge(left, right, on = 'HTID', how = 'inner'), dfs) #merge on volume ID

#drop NA's
volumes_scores = volumes_scores.dropna()


#Percentiles
print('Finding Percentiles')
volumes_scores['optimism_percentile'] = volumes_scores.optimism_score.rank(pct=True)
volumes_scores['industry_2_percentile'] = volumes_scores.industry_2.rank(pct=True)
volumes_scores['industry_3_percentile'] = volumes_scores.industry_3.rank(pct=True)


#Export Data
print('Exporting Data')
print(volumes_scores.head())
volumes_scores.to_csv('../temporary/volumes_scores.csv', index=False)