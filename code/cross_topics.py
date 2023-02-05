import os
import pandas as pd
import numpy as np
import itertools


#change wd to location of file
os.chdir(os.path.dirname(__file__))

#Import data
data = pd.read_csv('../input/20191007_topics.txt', sep = '\t', lineterminator = '\n', header=None)
data.drop(columns = 0, inplace = True)
data[1] = [string[string.rfind('/UK_data/')+9:-4] for string in data[1]]
data.columns = ['HTID'] + [i for i in range(1,61)]

#Function for getting cross-topic weights