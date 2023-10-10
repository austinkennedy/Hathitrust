#raw volume data, with scores for each of the 60 topics
raw_topic_scores = '../input/20191007_topics.txt'

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