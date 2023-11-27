import pandas as pd

print('Loading Data')
volume_topics = pd.read_csv('../temporary/topic_weights.csv')
metadata = pd.read_csv('../temporary/metadata.csv')

volumes = pd.merge(volume_topics, metadata, on = 'HTID', how = 'inner').drop(columns=['oclc','Year'])

sampling_window = 50
samples = 4

years = []
for year in range(1500, 1900, sampling_window):
    years.append(year)

n ={}
#find max volumes to sample
for year in years:
    df = volumes[(volumes['Year_rounded'] >= year) & (volumes['Year_rounded'] < (year+sampling_window))]
    n[year] = len(df)

#Choosing 1600 as sample size given small amount of volumes between 1500-1600
print(n)
sample_size = n[1600]
print('Sample size is: ' + str(sample_size))

print('Sampling')
for sample in range(1,samples+1):
    sampled_volumes = []
    for year in years:
        df = volumes[(volumes['Year_rounded'] >= year) & (volumes['Year_rounded'] < (year+sampling_window))]
        sampled_volumes.append(df.sample(n = min(sample_size, n[year])))
    
    df_sampled = pd.concat(sampled_volumes)
    sampled_htids = df_sampled['HTID']
    sampled_htids.to_csv('../temporary/sample_' + str(sample) + '.csv', index=False)




