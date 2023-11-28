import pandas as pd

volumes = pd.read_csv('../temporary/volumes.csv')
metadata = pd.read_csv('../temporary/metadata.csv')

window = 25

volumes = volumes.merge(metadata, on = 'HTID').drop(columns=['Year_rounded', 'oclc'])

years = []
for year in range(1500,1900,window):
    years.append(year)


tmp = []
for year in years:
    df = volumes[(volumes['Year'] >= year) & (volumes['Year'] < (year+window))]
    df['Religion_percentile'] = df.Religion.rank(pct=True)
    df['Science_percentile'] = df.Science.rank(pct=True) 
    df['PolitEcon_percentile'] = df['Political Economy'].rank(pct=True)

    df['percentile_sum'] = df['Religion_percentile'] + df['Science_percentile'] + df['PolitEcon_percentile']

    df['Religion_normalized'] = df['Religion_percentile']/df['percentile_sum']
    df['Science_normalized'] = df['Science_percentile']/df['percentile_sum']
    df['PolitEcon_normalized'] = df['PolitEcon_percentile']/df['percentile_sum']
    tmp.append(df)

volumes_percentiles = pd.concat(tmp)

volumes_reweighted = volumes_percentiles[['Religion_normalized', 'Science_normalized', 'PolitEcon_normalized', 'HTID']]
volumes_reweighted.rename(columns={'Religion_normalized': 'Religion', 'Science_normalized': 'Science', 'PolitEcon_normalized': 'Political Economy'}, inplace=True)

volumes_reweighted.to_csv('../temporary/volumes.csv', index=False)