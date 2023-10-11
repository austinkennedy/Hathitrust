# #raw volume data, with scores for each of the 60 topics
# #trained on full sample
# raw_topic_scores = '../input/20191007_topics.txt'


# #Allows for data cleaning specific to the dataset
# pre_1750 = False


# #topics themselves
# topic_info = '../input/20191007_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = [5,9,22,26,35,46,50,55,60]

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[4,12,52],
#     'Science':[7,8,41],
#     'Political Economy':[33,34,47]
#     }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/full_sample/'





##Uncomment this section for pre_1750 sample

#raw volume data, with scores for each of the 60 topics
#trained on full sample
raw_topic_scores = '../input/20230921_infer_topics.txt'


#Allows for data cleaning specific to the dataset
pre_1750 = True


#topics themselves
topic_info = '../input/20230623_keys.txt'

#innocuous topics to be eliminated
eliminated_topics = [2,19,26,28,35,52]

#check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

categories = {
    'Religion':[9,13,48],
    'Science':[37,45,54],
    'Political Economy':[5,18,29]
}

#set to 'False' to get triangle plots for every year instead of every half-century
half_century = True

output_folder = '../output/pre1750/'











