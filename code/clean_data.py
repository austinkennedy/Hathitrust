import pandas as pd
import pickle

samples = ['sample_1', 'sample_2', 'sample_3', 'sample_4']

sample_dict = {}

print('Importing Data')
#main dataset
topic_weights_full = pd.read_csv('../input/20191007_topics.txt', sep = '\t', lineterminator = '\n', header=None)

####data with 80 topics
topic_weights_80 = pd.read_csv('../input/20240414_topics.txt', sep = '\t', lineterminator= '\n', header=None)


# #subsamples
# for sample in samples:
#     sample_dict[sample] = pd.read_csv('../input/' + sample + '_infer_topics.txt', sep = '\t', lineterminator = '\n', header=None)
#     print(sample)
#     print(sample_dict[sample])

metapath = '../input/metadata.p'
metadata = pickle.load(open(metapath, 'rb'))

print('Cleaning Data')
topic_weights_full.drop(columns = 0, inplace = True)
topic_weights_full[1] = [string[string.rfind('/UK_data/')+9:-4] for string in topic_weights_full[1]]
topic_weights_full.columns = ['HTID'] + [i for i in range(1,len(topic_weights_full.columns))]
print(topic_weights_full)

topic_weights_80.drop(columns=0, inplace = True)
topic_weights_80[1] = [string[string.rfind('/all_2/')+7:-4] for string in topic_weights_80[1]]
topic_weights_80.columns = ['HTID'] + [i for i in range(1,len(topic_weights_80.columns))]
print(topic_weights_80)

# for sample in samples:
#     sample_dict[sample].drop(columns=0, inplace=True)
#     sample_dict[sample].columns = ['HTID'] + [i for i in range(1,len(sample_dict[sample].columns))]
#     sample_dict[sample]['HTID'] = [string[string.rfind('/all/')+5:-4] for string in sample_dict[sample]['HTID']]
#     print(sample)
#     print(sample_dict[sample])



metadata['Year_rounded'] = pd.to_numeric(metadata['Year'])
metadata['Year'] = pd.to_numeric(metadata['Year'], downcast='signed')
def fix_htid(row):
    return row['HTID'].replace(":","+").replace("/", "=")

metadata['HTID'] = metadata.apply(fix_htid, axis=1)


print('Exporting Data')
topic_weights_full.to_csv('../temporary/topic_weights_full.csv', index=False)
topic_weights_80.to_csv('../temporary/topic_weights_80_topics.csv', index=False)
metadata.to_csv('../temporary/metadata.csv', index=False)

# for sample in samples:
#     sample_dict[sample].to_csv('../temporary/topic_weights_' + sample + '.csv', index=False) 