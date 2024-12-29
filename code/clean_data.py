import pandas as pd
import pickle
import config

def clean_data(data, string_identifier):
    str_length = len(string_identifier)

    df = data.copy()
    df.drop(columns=0, inplace=True)
    df[1] = [string[string.rfind(string_identifier)+str_length:-4] for string in df[1]]
    df.columns = ['HTID'] + [i for i in range(1,len(df.columns))]
    return df

print('Importing Data')

topic_data = pd.read_csv(config.topic_data, sep = '\t', lineterminator = '\n', header = None)

metapath = '../input/metadata.p'
metadata = pickle.load(open(metapath, 'rb'))

translations = pd.read_csv('../input/translations.csv')

print('Cleaning Data')

topic_data_cleaned = clean_data(data = topic_data, string_identifier=config.string_identifier)

print(topic_data_cleaned)

metadata['Year_rounded'] = pd.to_numeric(metadata['Year'])
metadata['Year'] = pd.to_numeric(metadata['Year'], downcast='signed')
def fix_htid(row):
    return row['HTID'].replace(":","+").replace("/", "=")

metadata['HTID'] = metadata.apply(fix_htid, axis=1)

metadata = metadata.merge(translations, on= 'HTID', how = 'left')


print('Exporting Data')
topic_data_cleaned.to_csv('../temporary/topic_weights.csv', index = False)
metadata.to_csv('../temporary/metadata.csv', index=False)