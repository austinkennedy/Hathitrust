import pandas as pd
import pickle

print('Importing Data')
topic_weights_full = pd.read_csv('../input/20191007_topics.txt', sep = '\t', lineterminator = '\n', header=None)
sample_1 = pd.read_csv('../input/20231024_infer_topics.txt', sep = '\t', lineterminator = '\n', header=None)

metapath = '../input/metadata.p'
metadata = pickle.load(open(metapath, 'rb'))

print('Cleaning Data')
topic_weights_full.drop(columns = 0, inplace = True)
topic_weights_full[1] = [string[string.rfind('/UK_data/')+9:-4] for string in topic_weights_full[1]]
topic_weights_full.columns = ['HTID'] + [i for i in range(1,len(topic_weights_full.columns))]
print(topic_weights_full)

sample_1.drop(columns=0, inplace=True)
sample_1.columns = ['HTID'] + [i for i in range(1,len(sample_1.columns))]
sample_1['HTID'] = [string[string.rfind('/all/')+5:-4] for string in sample_1['HTID']]
print(sample_1)

metadata['Year_rounded'] = pd.to_numeric(metadata['Year'])
metadata['Year'] = pd.to_numeric(metadata['Year'], downcast='signed')
def fix_htid(row):
    return row['HTID'].replace(":","+").replace("/", "=")

metadata['HTID'] = metadata.apply(fix_htid, axis=1)


print('Exporting Data')
topic_weights_full.to_csv('../temporary/topic_weights_full.csv', index=False)
sample_1.to_csv('../temporary/topic_weights_sample_1.csv', index=False)
metadata.to_csv('../temporary/metadata.csv', index=False)
