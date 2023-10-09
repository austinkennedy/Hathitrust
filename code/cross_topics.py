import os
import pandas as pd
import numpy as np
import itertools

#Import data
data = pd.read_csv('../input/20191007_topics.txt', sep = '\t', lineterminator = '\n', header=None)
data.drop(columns = 0, inplace = True)
data[1] = [string[string.rfind('/UK_data/')+9:-4] for string in data[1]]
data.columns = ['HTID'] + [i for i in range(1,len(data.columns))]
print('Data dimensions:' + str(data.shape))

print(data.head)

data_pre1750 = pd.read_csv('../input/20230921_infer_topics.txt', sep = '\t', lineterminator='\n', header=None)
data_pre1750.drop(columns = 0, inplace = True)
data_pre1750[1] = [string[string.rfind('/all/')+5:-4] for string in data_pre1750[1]]
data_pre1750.columns = ['HTID'] + [i for i in range(1,len(data_pre1750.columns))]
print('Data (Pre-1750) dimensions:' + str(data_pre1750.shape))
print(data_pre1750.head)

#Function for getting cross-topic weights
def cross_multiply(df):
    #multiplies every column by every other column. Pass a dataframe with volumes as rows and topic weights as columns. 'HTID' column not required, but preferred

        
    i = 0
    ls = []

    if 'HTID' in df.columns:
        #handles data with a column for 'HTID'
        htids = df['HTID']
        df = df.drop(columns = 'HTID')
        ls.append(pd.DataFrame(htids, columns=['HTID']))

    names = df.columns.tolist() #get column names

    while i < len(df.columns):
        a = np.array(df.iloc[:,i])

        b = np.array(df.iloc[:,i+1:]) 

        c = (b.T * a).T #element-wise multiplication, multiplies topic weight by every other weight for each volume

        cols = [str(names[i]) + 'x' + str(j) for j in names[i+1:]] #column names, 'topic1 x topic2'
        
        
        ls.append(pd.DataFrame(c, columns=cols))

        i += 1

    cr = pd.concat(ls, axis = 1) #append across columns



    return cr


cross = cross_multiply(data)
cross_pre1750 = cross_multiply(data_pre1750)

print(cross.head)
print(cross_pre1750.head)

#export data
print('exporting cross-topics')
cross.to_csv('../temporary/cross_topics.csv', index = False)
cross_pre1750.to_csv('../temporary/cross_topics_pre1750.csv', index = False)
print('exporting topic weights')
data.to_csv('../temporary/topic_weights.csv', index = False)
data_pre1750.to_csv('../temporary/topic_weights_pre1750.csv', index = False)