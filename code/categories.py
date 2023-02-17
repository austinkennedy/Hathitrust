#import packages
print('Loading Packages')
import os
import pandas as pd
import itertools
from iteration_utilities import unique_everseen
from math import comb

#Load Data
print('Loading Data')
volume_weights = pd.read_csv("../temporary/topic_weights.csv")
cross = pd.read_csv('../temporary/cross_topics.csv')
topics = pd.read_csv('../input/20191007_keys.txt', sep = '\t', lineterminator='\n', header=None)

#fix topic numbers
topics.drop(columns=0, inplace=True)
topics['topic_number'] = list(range(1,61))

group = [5,9,22,26,35,46,50,55,60] #innocuous topics to be eliminated

#functions
def cross_share(data):
    df = data.copy() #Won't modify original object

    if 'HTID' in df.columns:
        df.drop(columns = ['HTID'], inplace=True)
    
    share = df.sum(axis = 0) / sum(df.sum(axis=0)) #numerator: sum down across rows, denominator: sum the sum of rows to get total of all cross-topics
    return share

def get_shares(top = topics, omit = None, length = 3):
    #'topics' is a list or dataframe of topics, where each row corresponds to a topic
    #'omit' is a list of topics to omit, should be a list of numbers
    #'length' is the size of the categories (i.e. how many topics should make up a category), default 3

    n = len(top) #get number of topics
    topic_numbers = list(topics['topic_number']) # generate topic numbers

    if omit is not None:
        topic_numbers = [i for i in topic_numbers if i not in omit] #remove innocuous topics
    
    topic_numbers.sort() #itertools.combinations needs sorted list
    combos = list(itertools.combinations(topic_numbers, r = length)) #create combinations of desired length

    combo_sets = [set(i) for i in combos] #get set of topic numbers for each row, i is each combo, contained in a tuple

    cross_combos = [list(itertools.combinations(i,2)) for i in combos]#gets every combination of elements in row from combos, i.e. for (1,2,3) gets (1,2),(1,3),(2,3)
    cross_combos = [['x'.join(map(str, i)) for i in c] for c in cross_combos] #joins each topic pair with 'x' to reference 'shares'
    cross_shares = [[shares[str(i)] for i in c] for c in cross_combos] #get share for each element
    cross_sum = [sum(i) for i in cross_shares] #sum each row

    #column names
    topic_names = ['topic' + str(i) for i in range(1, length+1)]
    cross_names = ['combination' + str(i) for i in range(1, comb(length, 2)+1)] #'math.comb' gives the number of combinations, not the combinations themselves
    share_names = ['share' + str(i) for i in range(1, comb(length, 2)+1)]

    #convert to dataframes since each are lists of tuples, easier to join
    combos = pd.DataFrame(combos, columns=topic_names)
    combo_sets = pd.DataFrame(pd.Series(combo_sets), columns=['Sets'])
    cross_combos = pd.DataFrame(cross_combos, columns=cross_names)
    cross_shares = pd.DataFrame(cross_shares, columns=share_names)
    cross_sum = pd.DataFrame(cross_sum, columns=['Sum'])


    tmp = pd.concat([combos, combo_sets, cross_combos, cross_shares, cross_sum], axis = 1)
    df = pd.DataFrame(tmp)
    # df = pd.DataFrame(tmp, columns=[topic_names, cross_names, share_names, 'Sum'])

    return df

def distinct_categories(data):
    #algorithm to get distinct categories
    #takes the output of 'get_shares' function and finds unique categories
    #'Sets' in 'data' is a column with the set of topics in each row

    data.sort_values('Sum', ascending = False, inplace = True) #Make sure values are sorted

    seen = set([]) #create empty set
    unique = [] #list for appending unique rows

    for ind, row in data.iterrows():
        if bool(row['Sets'] & seen): #checks if any elements in 'Set' are in 'seen', if so, move to next row
            pass
        else:
            unique.append(row) #if the set is unique, grab row
            seen.update(row['Sets']) #add set of topics to 'seen'

    df = pd.DataFrame(unique)

    return(df)

print('Calculating shares')
shares = cross_share(cross)

print('Getting categories')
clusters = get_shares(top = topics, omit = group, length = 3)

print('Finding distinct categories')
clusters_corpus = distinct_categories(clusters)
print(clusters_corpus)

print('Exporting Topics')
topics.to_csv('../temporary/topics.csv', index=False)




