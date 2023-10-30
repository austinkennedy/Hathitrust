# #raw volume data, with scores for each of the 60 topics
# #trained on full sample
# topic_weights = 'full'

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

##Uncomment this section for Sample 1
topic_weights = 'sample_1'

#topics themselves
topic_info = '../input/20231019_keys.txt'

#innocuous topics to be eliminated
eliminated_topics = []

#check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

categories = {
    'Religion':[14,18,40],
    'Science':[21,36,42],
    'Political Economy':[9,16,35]
    }

#set to 'False' to get triangle plots for every year instead of every half-century
half_century = True

output_folder = '../output/sample_1/'

# ##Uncomment this section for pre_1750 sample

# #raw volume data, with scores for each of the 60 topics
# #trained on full sample
# topic_weights = 'sample_1'


# #topics themselves 
# topic_info = '../input/20230623_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = [3,19,26,28,35,52]

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[2,16,53],
#     'Science':[11,46,60],
#     'Political Economy':[1,15,30]
# }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/pre1750/'











