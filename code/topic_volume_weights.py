
#Packages
print('Loading Packages')
import pandas as pd
import itertools
import os
import numpy as np
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
from operator import itemgetter
import config


#Load Data
print('Loading Data')
moving_average_shares = pd.read_csv('../temporary/moving_average_shares.csv', index_col='Unnamed: 0')
topics = pd.read_csv('../temporary/topics.csv')
volume_topics = pd.read_csv('../temporary/topic_weights.csv')

#volume metadata
metadata = pd.read_csv('../temporary/metadata.csv')

#match volume years and fix to be compatible with category weights
volume_topics = pd.merge(volume_topics, metadata, on = 'HTID', how = 'inner').drop(columns=['oclc','Year'])


def fix_years(df):
    for ind,row in df.iterrows():
        if row['Year_rounded'] > 1890:
            df.at[ind, 'Year_rounded'] = 1890
        elif row['Year_rounded'] < 1510:
            df.at[ind, 'Year_rounded'] = 1510

    return df

volume_topics = fix_years(volume_topics)

#Functions
def category_shares(topics, ctshares, year, categories):
    #'categories' needs to be a dict with keys as category names and values as a list of category topics, i.e. 'Category': [1,2,3]
    #'ctshares' needs to be a dataframe with cross_topic shares as values, years as columns, and indices as 'topic1 x topic2', e.g. '3x4'
    #topics must have a column 'topic_number' with the number corresponding to each topic
    tmp_dict = {}
    
    topic_numbers = list(topics['topic_number'])
    shares = ctshares[str(year)] #grab column with cross-topic shares for the year

    for name,category in categories.items():
        print(year)
        print(category)
        combos = {topic:list(itertools.product([topic], set(category) - set([topic]))) for topic in topic_numbers} #This gets the appropriate combo of each topic and the topics in each category, so for topic 1 and 'Political Economy', gets [(1,33),(1,34),(1,47)]

        cross_combos = {key:['x'.join(map(str,sorted(i))) for i in value] for key,value in combos.items()} #sorts topic pairs so that they will be called from 'shares' correctly, and joins with 'x'


        cross_shares = {key:[shares[str(i)] for i in value] for key,value in cross_combos.items()} #get share value from 'shares'

        cross_sum = {key:sum(value) if key not in category else sum(value)*1.5 for key,value in cross_shares.items()} #sum shares for the topic and topics in category. If topic in category, multiply by 1.5 since it will be missing one topic pair, e.g. for topic 33 it just has 33x34 and 33x47, so must be scaled correctly. NOT ROBUST YET TO OTHER SIZES THAN 3 TOPICS PER CATEGORY.

        tmp_dict[name] = cross_sum

        #get a look into algorithm
        if year == 1800:
            print(combos)
            print(cross_combos)
            print(cross_shares)
            print(cross_sum)
            


    df = pd.DataFrame.from_dict(tmp_dict)
    

    total = df.sum(axis=1) #get total of category scores
    cat_shares = df.div(total, axis=0) #divide by total, so that Religion + Science + Political Economy = 1
    return cat_shares

def make_dir(path):
            #check if directory in path exists, if not create it
    if not os.path.exists(path):
        os.makedirs(path)

        # Create .gitignore file
        gitignore_path = os.path.join(path, ".gitignore")
        with open(gitignore_path, "w") as gitignore_file:
            gitignore_file.write("*\n*/\n!.gitignore\n")
        print(f".gitignore file created.") 

years=[]
for year in range(1510,1891):
    years.append(year)

print('Getting topic scores')
#get topic category scores for every year
topic_shares = {}

for year in years:
    topic_shares[year] = category_shares(topics = topics, ctshares = moving_average_shares, year = year, categories = config.categories)




print('Getting volume scores')
#get category scores for each volume
ls = []
topic_columns = [str(i) for i in topics['topic_number']] #columns need to be called as string
for ind,row in volume_topics.iterrows():
    year = int(row['Year_rounded']) #year of volume
    a = np.array(row[topic_columns]) #row of topic weights for each volume, colnames need to correspond to topic numbers
    b = np.array(topic_shares[year]) #topic category weights by year

    c = np.array(np.matmul(a,b)) #matrix multiplication--multiplies volume topic-weights by topic category weights, summed by each category to get category weights for each volume for each row --> (1,60)x(60,3) --> (1,3)
    c = c[None,:] #reshape array 
    tmp = pd.DataFrame(c, columns = topic_shares[year].columns)
    tmp['HTID'] = row['HTID']
    ls.append(tmp)

volumes = pd.concat(ls, axis = 0)
volumes

#export
volumes.to_csv('../temporary/volumes.csv', index=False)

#Topic ternary plots-much easier to do it within this script so as to not have to export/import dictionary of dataframes

#Get colors of each topic
#Uses 1850 as a basis for whether topic is "science, religion, or politics"
for year in years:
    topic_shares[year]['Color'] = topic_shares[1850][['Religion','Science','Political Economy']].idxmax(axis=1) #finds highest share for each topic


if config.half_century is True:
    years = []
    for year in range(1550, 1891, 50):
        years.append(year)

make_dir(config.output_folder + 'topic_triangles/')

print('Ternary Plots')
#create and export ternary plots
for year in years:
    fig = px.scatter_ternary(topic_shares[year],
                                a='Religion', b = 'Political Economy', c = 'Science',
                                color = 'Color',
                                color_discrete_map = {'Science':'green', 'Religion': 'blue', 'Political Economy':'red'},
                                template = 'simple_white',
                                symbol = "Color",
                                symbol_map = {'Science': 'circle','Religion': 'cross', 'Political Economy': 'triangle-up'})

    fig.update_traces(showlegend=False, marker = {'size': 10})
    fig.update_layout(title_text = str(year), title_font_size=30, font_size=20)

    if year == 1850:
        #add legend and adjust size for 1850
        fig.update_traces(showlegend=True)
        fig.update_layout(legend = dict(y=0.5), legend_title_text = 'Legend')
        fig.write_image(config.output_folder + 'topic_triangles/' + str(year) +'.png', width = 900)
    else:
        fig.write_image(config.output_folder + 'topic_triangles/' + str(year) +'.png')







