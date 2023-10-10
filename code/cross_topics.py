print('Loading Packages')
import pandas as pd
import numpy as np
import config

#Import data
print('Loading Data')

data = pd.read_csv(config.raw_topic_scores, sep = '\t', lineterminator = '\n', header=None)

if config.pre_1750 is False:
    data.drop(columns = 0, inplace = True)
    data[1] = [string[string.rfind('/UK_data/')+9:-4] for string in data[1]]
    data.columns = ['HTID'] + [i for i in range(1,len(data.columns))]
    print('Data dimensions:' + str(data.shape))
    print(data.head)

elif config.pre_1750 is True:
    data.drop(columns = 0, inplace = True)
    data[1] = [string[string.rfind('/all/')+5:-4] for string in data[1]]
    data.columns = ['HTID'] + [i for i in range(1,len(data.columns))]
    print('Data (Pre-1750) dimensions:' + str(data.shape))
    print(data.head)

else:
    print('Please set pre_1750 to True or False')

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

print(cross.head)

#export data
print('exporting cross-topics')
cross.to_csv('../temporary/cross_topics.csv', index = False)

print('exporting topic weights')
data.to_csv('../temporary/topic_weights.csv', index = False)
