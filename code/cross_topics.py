print('Loading Packages')
import pandas as pd
import numpy as np
import config

#Import data
print('Loading Data')

data = pd.read_csv('../temporary/topic_weights_' + config.topic_weights + '.csv', sep = '\t', lineterminator = '\n', header=None)

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


# described = data.describe()
# described.to_csv(config.output_folder + 'data_descriptive_stats.csv')

cross = cross_multiply(data)

print(cross.head)

#export data
print('exporting cross-topics')
cross.to_csv('../temporary/cross_topics.csv', index = False)

print('exporting topic weights')
data.to_csv('../temporary/topic_weights.csv', index = False)
