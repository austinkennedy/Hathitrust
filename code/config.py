#raw volume data, with scores for each of the 60 topics
#trained on full sample
topic_weights = 'full'

#topics themselves
topic_info = '../input/20191007_keys.txt'

#innocuous topics to be eliminated
eliminated_topics = [5,9,22,26,35,46,50,55,60]

#check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

categories = {
    'Religion':[4,12,52],
    'Science':[7,8,41],
    'Political Economy':[33,34,47]
    }

#set to 'False' to get triangle plots for every year instead of every half-century
half_century = True

output_folder = '../output/full_sample/'

# ##Uncomment this section for Sample 1
# topic_weights = 'sample_1'

# #topics themselves
# topic_info = '../input/20231019_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = []

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[4,14,40],
#     'Science':[21,35,36],
#     'Political Economy':[33,52,57]
#     }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/sample_1/'

#####Uncomment for sample 2

# topic_weights = 'sample_2'

# #topics themselves
# topic_info = '../input/20231019_sample_2_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = []

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[4,8,60],
#     'Science':[31,49,56],
#     'Political Economy':[12,19,32]
#     }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/sample_2/'

#####Uncomment for sample 3

# topic_weights = 'sample_3'

# #topics themselves
# topic_info = '../input/20231019_sample_3_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = []

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[4,23,45],
#     'Science':[20,42,54],
#     'Political Economy':[22,36,49]
#     }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/sample_3/'

#####Uncomment for sample 4

# topic_weights = 'sample_4'

# #topics themselves
# topic_info = '../input/20231019_sample_4_keys.txt'

# #innocuous topics to be eliminated
# eliminated_topics = []

# #check before running 'topic_volume_weights.py'. The classification of the output from 'categories.py' into 'Religion', 'Science', and 'Political Economy' is subjective and needs to be manually classified.

# categories = {
#     'Religion':[29,35,57],
#     'Science':[11,12,36],
#     'Political Economy':[9,37,41]
#     }

# #set to 'False' to get triangle plots for every year instead of every half-century
# half_century = True

# output_folder = '../output/sample_4/'





