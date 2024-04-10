print('Loading Packages')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.express as px
import os
import statistics
import config
plt.style.use('seaborn-white')

print('Loading Data')
volumes = pd.read_csv('../temporary/volumes_scores.csv')

#Global Options
split = 1/3

categories = ['Religion', 'Science', 'Political Economy']

#create sequence of years
years=[]
for year in range(1510,1891):
    years.append(year)

#functions
def category_averages(data, year, category):
    cat_vols = data[data['Category'] == category]
    cols = cat_vols[['Religion', 'Science', 'Political Economy']]
    means = np.array(cols.mean(axis = 0))
    means = means[None,:]
    tmp = pd.DataFrame(means, columns=cols.columns)
    tmp['Year'] = year
    # tmp['Volumes'] = len(cat_vols)
    return tmp   

def make_dir(path):
            #check if directory in path exists, if not create it
    if not os.path.exists(path):
        os.makedirs(path)

        # Create .gitignore file
        gitignore_path = os.path.join(path, ".gitignore")
        with open(gitignore_path, "w") as gitignore_file:
            gitignore_file.write("*\n*/\n!.gitignore\n")
        print(f".gitignore file created.") 

#Categorize Volumes
volumes['Category'] = volumes[['Religion','Science','Political Economy']].idxmax(axis=1) #Finds highest share for each topic

category_counts_by_year = volumes.groupby(['Year', 'Category']).size().unstack(fill_value=0).reset_index()
print(category_counts_by_year)

print(category_counts_by_year)
# print total amount in each category
for category in categories:
    n = len(volumes[volumes['Category'] == category])
    print(category + ' Volumes: ' + str(n))

    
volumes_time = {key: [] for key in categories}

volume_count = {}
moving_volumes = {}
avg_progress = {}

print('Getting Category Averages')
#Get averages for volumes in category
for year in years:
    df = volumes[(volumes['Year'] >= (year-10)) & (volumes['Year'] <= (year+10))]
    for category in categories:
        volumes_time[category].append(category_averages(df, year, category))

    volume_count[year] = len(df)
    moving_volumes[year] = df
    avg_progress[year] = statistics.mean(df['progress_percentile_main'])


for category in categories:
    volumes_time[category] = pd.concat(volumes_time[category])
    counts = category_counts_by_year[['Year', category]].rename(columns = {category: 'Volumes'})
    volumes_time[category] = volumes_time[category].merge(counts, on = 'Year')
    print(volumes_time[category].head())
    volumes_time[category]['Volumes_rolling'] = volumes_time[category]['Volumes'].rolling(window = 20, min_periods=1, center=True).mean()
    print(volumes_time[category].head())

make_dir(config.output_folder + 'volumes_over_time/')

print('Category Plots')
for category in categories:
    df = volumes_time[category]

    fig, (ax1) = plt.subplots(1,1)
    ax1.plot(df['Year'], df['Religion'], color = 'b', label = 'Religion', linestyle = 'dashdot')
    ax1.plot(df['Year'], df['Science'], color = 'g', label = 'Science', linestyle = 'dashed')
    ax1.plot(df['Year'], df['Political Economy'], color = 'r', label = 'Political Economy', linestyle = 'dotted')
    ax1.legend(loc = 'upper right')
    plt.ylim([0,0.8])
    ax1.title.set_text(category + ' Volumes')

    ax2 = ax1.twinx()
    ax2.set_ylabel('# of volumes')
    ax2.plot(df['Year'], df['Volumes_rolling'], color = 'black', label = 'Total Volumes')
    ax2.legend(loc = 'upper center')
    plt.ylim([0,2500])

    fig.savefig(config.output_folder + 'volumes_over_time/' + category + '.png', dpi = 200)

#Volume count figure, raw
volume_count_raw = {}
for year in years:
    if len(volumes[volumes['Year'] == year]) != 0:
        volume_count_raw[year] = len(volumes[volumes['Year'] == year])
    else:
        volume_count_raw[year] = 0
count_raw = pd.DataFrame(volume_count_raw.items(), columns = ['Year', 'Count'])

fig, (ax1) = plt.subplots(1,1)
ax1.plot(count_raw['Year'], count_raw['Count'], color = 'darkblue', label = 'Volume Count')
ax1.legend(loc = "upper left")
ax1.set_xlabel('Year')
fig.savefig(config.output_folder + 'Total_Volumes_Raw.png', dpi = 200)

#Volume count figure, using moving avg
count = pd.DataFrame(volume_count.items(), columns=['Year', 'Count'])
count['Count_rolling'] = count['Count'].rolling(window = 20, min_periods=1, center=True).mean()

fig, (ax1) = plt.subplots(1,1)
ax1.plot(count['Year'], count['Count_rolling'], color = "darkblue", label = "Volume Count")
ax1.legend(loc = "upper right")
ax1.set_xlabel('Year')
ax1.set_yticks([0,25000, 50000, 75000])
ax1.set_yticklabels(["0", "25,000", "50,000", "75,000"])
plt.ylim([0,75000])
fig.savefig(config.output_folder + 'volumes_over_time/total_volumes.png', dpi = 200)

#Average Sentiment Over Time (Smoothed)
progress = pd.DataFrame(avg_progress.items(), columns=['Year', 'avg_progress'])

fig, (ax1) = plt.subplots(1,1)
ax1.plot(progress['Year'], progress['avg_progress'], color = 'crimson', label = 'Average Progress Score (Percentile)')
ax1.legend(loc = 'upper right')
ax1.set_xlabel('Year')
ax1.set_yticks([0,0.25,0.5,0.75,1])
fig.savefig(config.output_folder + 'volumes_over_time/' + 'avg_progress.png', dpi = 200)

#Average Sentiment Over Time (Raw)

avg_progress_raw = {}
for year in years:
    if len(volumes[volumes['Year'] == year]) != 0:
        avg_progress_raw[year] = statistics.mean(volumes[volumes['Year'] == year]['progress_percentile_main'])
    else:
        avg_progress_raw[year] = np.nan
progress_raw = pd.DataFrame(avg_progress_raw.items(), columns = ['Year', 'avg_progress'])
fig, (ax1) = plt.subplots(1,1)
ax1.plot(progress_raw['Year'], progress_raw['avg_progress'], color = 'crimson', label = 'Average Progress Score (Percentile)')
ax1.legend(loc = 'upper right')
ax1.set_xlabel('Year')
ax1.set_yticks([0,0.25,0.5,0.75,1])
fig.savefig(config.output_folder + 'volumes_over_time/' + 'avg_progress_raw.png', dpi = 200)

print(min(volumes['progress_percentile_main']))

# #Ternary plots

if config.half_century is True:
    years = []
    for year in range(1550, 1891, 50):
        years.append(year)

def ternary_plots(data, color, filepath, legend_title, years = years, grayscale = False, size = None, decreasing_scale = False, show_legend = True):
    #'data' needs to be a dictionary of dataframes, with volumes as rows, and columns 'Religion', 'Political Economy', and 'Science'
    #'color': which variable color of dots will be based on
    #'path': directory to save output figures
    #'years': a list of years you want figures for
    #'grayscale': True if you want grayscale, will reverse color scale as well
    #'size': variable that determines size of dots, None by default
    #'increasing_scale': If 'True', size of dots will be bigger with bigger values of the 'size' variable

    s = str(size)

    for year in years:
        df = data[year]
        print(year)

        if decreasing_scale is True:
            df['size_percentile_r'] = 1 - df['industry_3_percentile']
            size = 'size_percentile_r'


        fig = px.scatter_ternary(df, a = 'Religion', b = 'Political Economy', c = 'Science',
                                 color = color,
                                 size = size,
                                 size_max=13,
                                 range_color=[0,1])
        
        fig.update_layout(title_text = str(year),
                        title_font_size=30,
                        font_size=20,
                        margin_l = 110,
                        legend_title_side = 'top',
                        coloraxis_colorbar_title_text = 'Percentile',
                        coloraxis_colorbar_title_side = 'top'
                        )
        
        fig.update_ternaries(bgcolor="white",
                        aaxis_linecolor="black",
                        baxis_linecolor="black",
                        caxis_linecolor="black"
                        )
        
        if grayscale is True:
            fig.update_layout(coloraxis = {'colorscale':'gray'})

        fig.update_traces(
            showlegend = False
        )

        #check if directory in path exists, if not create it
        make_dir(path = filepath)

        if year == 1850 and show_legend is True:   
            fig.write_image(filepath + str(year) + '.png', width=900) #included because wider format needed for color scale
        
        else:
            fig.update(layout_coloraxis_showscale=False) #removes colorbar
            fig.write_image(filepath + str(year) + '.png') #only works with kaleido 0.1.0 for some reason, use 'conda install python-kaleido=0.1.0post1' on PC, also uses plotly 5.10.0
        
        # Uncomment for no legend at all
        # fig.update(layout_coloraxis_showscale=False) #removes colorbar
        # fig.write_image(path + str(year) + '.png') #only works with kaleido 0.1.0 for some reason, use 'conda install python-kaleido=0.1.0post1' on PC, also uses plotly 5.10.0

print(volumes)

# print('Original Progress Triangles, color')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_original',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_original/color/')

# print('Original Progress Triangles, grayscale')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_original',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_original/grayscale/',
#               grayscale=True)

# print('Main Progress Triangles, color')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_main/color/')

# print('Main Progress Triangles, grayscale')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_main/grayscale/',
#               grayscale=True)

# print('Secondary Progress Triangles, color')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_secondary',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_secondary/color/')

# print('Secondary Progress Triangles, grayscale')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_secondary',
#               legend_title='Progress (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_secondary/grayscale/',
#               grayscale=True)

# print('Optimistic Triangles, color')
# ternary_plots(data = moving_volumes,
#               color = 'optimistic_percentile',
#               legend_title='Optimistic (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/optimistic/')

# print('Industry Triangles, color')
# ternary_plots(data = moving_volumes,
#               color = 'industry_3_percentile',
#               legend_title='Industry (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/industry/color/')

# print('Industry Triangles, grayscale')
# ternary_plots(data = moving_volumes,
#               color = 'industry_3_percentile',
#               legend_title='Industry (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/industry/grayscale/',
#               grayscale=True)


# print('Industry Triangles (1643), color')
# ternary_plots(data = moving_volumes,
#               color = 'industry_1643_percentile',
#               legend_title='Industry (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/industry_1643/color/')

# print('Industry Triangles (1643), grayscale')
# ternary_plots(data = moving_volumes,
#               color = 'industry_1643_percentile',
#               legend_title='Industry (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/industry_1643/grayscale/',
#               grayscale=True)

# print('Size based, increasing')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               size = 'industry_3_percentile',
#               legend_title='Progress (Percentile)',
#               show_legend = False,
#               filepath = config.output_folder + 'volume_triangles/industry_optimism/increasing_scale/')

# print('Size based, decreasing')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               size = 'industry_3_percentile',
#               legend_title='Progress (Percentile)',
#               decreasing_scale=True,
#               filepath = config.output_folder + 'volume_triangles/industry_optimism/decreasing_scale/')

# print('Size based, increasing, 1643')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               size = 'industry_1643_percentile',
#               legend_title='Progress (Percentile)',
#               show_legend = False,
#               filepath = config.output_folder + 'volume_triangles/industry_optimism_1643/increasing_scale/')

# print('Size based, decreasing, 1643')
# ternary_plots(data = moving_volumes,
#               color = 'progress_percentile_main',
#               size = 'industry_1643_percentile',
#               legend_title='Progress (Percentile)',
#               decreasing_scale=True,
#               show_legend = False,
#               filepath = config.output_folder + 'volume_triangles/industry_optimism_1643/decreasing_scale/')


# print('Progress minus regression, original')
# ternary_plots(data=moving_volumes,
#               color='progress_regression_percentile_original',
#               legend_title='Progress - Regression (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_regression_original/')

# print('Progress minus regression, main')
# ternary_plots(data=moving_volumes,
#               color='progress_regression_percentile_main',
#               legend_title='Progress - Regression (Percentile)',
#               filepath = config.output_folder + 'volume_triangles/progress_regression_main/')
 
# print('Progress minus regression, secondary')
# ternary_plots(data=moving_volumes,
#               color='progress_regression_percentile_secondary',
#               legend_title='Progress - Regression',
#               filepath = config.output_folder + 'volume_triangles/progress_regression_secondary/')

