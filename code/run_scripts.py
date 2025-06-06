import subprocess

# Run Python Scripts
print('Running clean_data.py')
subprocess.run(['python', 'clean_data.py'])

print('Running cross_topics.py')
subprocess.run(['python', 'cross_topics.py'])

print('Running categories.py')
subprocess.run(['python', 'categories.py'])

print('Running shares.py')
subprocess.run(['python', 'shares.py'])

print('Running topic_volume_weights.py')
subprocess.run(['python', 'topic_volume_weights.py'])

print('Running volume_data.py')
subprocess.run(['python', 'volume_data.py'])

print('Running volume_figures.py')
subprocess.run(['python', 'volume_figures.py'])

print('Running progress_econometrics.R')
subprocess.run(['Rscript', 'progress_econometrics.R'])

print('Running industry_econometrics.R')
subprocess.run(['Rscript', 'industry_econometrics.R'])

# print('Running subtriangles.R')
# subprocess.run(['Rscript', 'subtriangles.R'])

# print('Running biscale_triangles.R')
# subprocess.run(['Rscript', 'biscale_triangles.R'])