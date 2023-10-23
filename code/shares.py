#Packages
print('Loading Packages')
import os
import pandas as pd
import pickle

print('Loading Data')
#Load Data
cross = pd.read_csv('../temporary/cross_topics.csv')
metadata = pd.read_csv('../temporary/metadata.csv')

#merge years onto volumes
cross = pd.merge(cross, metadata, on='HTID', how='inner').drop(columns = ['oclc', 'Year'])
print(cross.head())

#create sequence of years
years=[]
for year in range(1510,1891):
    years.append(year)


def moving_shares(data, year):
    #get 20-year moving average of data
    df = data[(data['Year_rounded'] >= (year-10)) & (data['Year_rounded'] <= (year+10))] #grab volumes within +/- 10 year window
    df.drop(columns = 'Year_rounded', inplace=True)

    if 'HTID' in df.columns:
        df.drop(columns = ['HTID'], inplace=True)

    print(df)

    share = df.sum(axis=0) / sum(df.sum(axis=0)) #numerator gets sum of each cross-topic across all volumes, denominator gets sum of all cross-topics over all volumes in window

    return share

print('Calculating Moving Average Shares')
ct_shares = {}
for year in years:
    ct_shares[year] = moving_shares(cross, year)

moving_average_shares = pd.DataFrame.from_dict(ct_shares)

print('Exporting data')
print(moving_average_shares.head())
moving_average_shares.to_csv('../temporary/moving_average_shares.csv', index=True)



