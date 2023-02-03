import os
import pandas as pd

#change wd to location of file
os.chdir(os.path.dirname(__file__))

#Import data
volume_topics = pd.read_csv('../input/20191007_topics.txt', sep = '\t', lineterminator = '\n', header=None)
