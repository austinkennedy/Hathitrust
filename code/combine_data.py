#packages

print("Loading packages")

import os
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from scipy import stats

print(os.getcwd())

volume_topics = '../input/20191007_topics.txt'

volume_industry_2_3 = pd.read_csv('../input/industry_scores_2_3.csv')
volume_industry_2_3 = volume_industry_2_3.rename(columns = {volume_industry_2_3.columns[0]: 'HTID', '2-vote':'industry_2', '3-vote': 'industry_3'})
volume_industry_2_3['HTID'] = volume_industry_2_3['HTID'].map(lambda x: x.rstrip('.txt')) #remove '.txt' at the end of each string for HTIDs
print('volume_industry_2_3:' + str(volume_industry_2_3.shape))


volume_industry = pd.read_csv('../input/industry_scores.csv')
volume_industry = volume_industry.rename(columns = {'Unnamed: 0':'HTID', 'Weighted Sum': 'industry_full'})
volume_industry = volume_industry.drop(columns = ['Path', 'year'])
volume_industry['HTID'] = volume_industry['HTID'].map(lambda x: x.rstrip('.txt')) #remove '.txt' at the end of each string for HTIDs
print('volume_industry:' + str(volume_industry.shape))

volume_weights = pd.read_csv('../input/volume_weights.csv', index_col = [0])
print('volume_weights:' + str(volume_weights.shape))

volume_sentiment = pd.read_csv('../Input/Sentiment Analysis Results (Thesaurus List).csv')
volume_sentiment = volume_sentiment.merge(volume_industry, left_on="HTID", right_on = "HTID")
volume_sentiment = volume_sentiment.merge(volume_industry_2_3, left_on = "HTID", right_on = "HTID")

print("Dimensions (volume_sentiment):" + str(volume_sentiment.shape))


data = pd.read_csv(volume_topics, sep = '\t', lineterminator = '\n', header=None)
data.drop(columns = 0, inplace = True)
data[1] = [string[string.rfind('/UK_data/')+9:-4] for string in data[1]]
data.columns = ['HTID'] + [i for i in range(1,61)]
print("Dimensions ('Data'): " + str(data.shape))
# htids = data['HTID']
# data = data.drop(columns=['HTID'])
# volume_weights['HTID'] = data['HTID']

metapath = "../Input/metadata.p"
metadata = pickle.load(open(metapath, 'rb'))

metadata['Year_rounded'] = pd.to_numeric(metadata['Year'])
metadata['Year'] = pd.to_numeric(metadata['Year'], downcast='signed')

def fix_htid(row):
    return row['HTID'].replace(":","+").replace("/", "=")

# with open('../Input/meta_weights.p', 'rb') as fp:
#     moving_shares = pickle.load(fp)

metadata['HTID'] = metadata.apply(fix_htid, axis=1)

df = data.merge(volume_sentiment, left_on='HTID', right_on='HTID')
df3 = volume_weights.merge(volume_sentiment, left_on='HTID', right_on='HTID')
df3 = pd.merge(df3, metadata, on = "HTID", how = 'inner').drop(columns = ['oclc', 'Year'])
df3 = df3.drop(columns=['HTID', 'Unnamed: 0', 'key'])

df = pd.merge(df, metadata, on='HTID', how='inner').drop(columns = ['oclc', 'Year'])
# df['Year_rounded'] = df2['Year_rounded']
df = df.drop(columns=['HTID', 'Unnamed: 0', 'key'])
print(df.head())

a = df3['percent_optimistic'] + df3['percent_progress'] #Total Optimism
b = df3['percent_pessimism'] + df3['percent_regression'] #Total Pessimism
c = a - b #Net Optimism Score
df3['Optimism'] = c
# df3['Year_rounded'] = df['Year_rounded']
df3 = df3.drop(columns = ['percent_optimistic', 'percent_progress', 'percent_pessimism', 'percent_regression'])
print(df3.head())
print('df3 (including NAs):' + str(df3.shape))

years = []
for year in range(1510,1891):
    years.append(year)

df3 = df3.dropna()

nan_count = df3.isna().sum().sum()
print("NA's: " + str(nan_count))
#Finding percentiles
opt = df3['Optimism']
p = stats.rankdata(opt, "average")/len(opt) #assign each "optimism" score to its percentile
df3['optimism_percentile'] = p

ind = df3['industry_full']
p1 = stats.rankdata(ind, "average")/len(ind)
df3['industry_full_percentile'] = p1

ind2 = df3['industry_2']
p2 = stats.rankdata(ind2, "average")/len(ind2)
df3['industry_2_percentile'] = p2

ind3 = df3['industry_3']
p3 = stats.rankdata(ind3, "average")/len(ind3)
df3['industry_3_percentile'] = p3

#Rename 'Politics' to 'Political Economy'
df3.rename(columns ={'Politics':'Political.Economy'}, inplace=True)

print(df3.head())
print("Dimensions (cleaned):" + str(df3.shape))
print("Columns:" + str(df3.keys()))

#export data
df3.to_csv("../temporary/volumes_opt_industry_all.csv")



















