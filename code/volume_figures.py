print('Loading Packages')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.express as px
plt.style.use('seaborn-white')

print('Loading Data')
volumes = pd.read_csv('../temporary/volumes_scores.csv')

#Global Options
split = 1/3
half_century = True

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
    tmp['Volumes'] = len(cat_vols)
    return tmp    

#Categorize Volumes
volumes['Category'] = volumes[['Religion','Science','Political Economy']].idxmax(axis=1) #Finds highest share for each topic

# print total amount in each category
for category in categories:
    n = len(volumes[volumes['Category'] == category])
    print(category + ' Volumes: ' + str(n))

    
volumes_time = {key: [] for key in categories}

volume_count = {}
moving_volumes = {}

print('Getting Category Averages')
#Get averages for volumes in category
for year in years:
    df = volumes[(volumes['Year'] >= (year-10)) & (volumes['Year'] <= (year+10))]
    for category in categories:
        volumes_time[category].append(category_averages(df, year, category))

    volume_count[year] = len(df)
    moving_volumes[year] = df

for category in categories:
    volumes_time[category] = pd.concat(volumes_time[category])

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
    ax2.plot(df['Year'], df['Volumes'], color = 'black', label = 'Total Volumes')
    ax2.legend(loc = 'upper center')
    plt.ylim([0,50000])

    fig.savefig('../output/volumes_over_time/' + category + '.png', dpi = 200)


#Volume count figure
count = pd.DataFrame(volume_count.items(), columns=['Year', 'Count'])

fig, (ax1) = plt.subplots(1,1)
ax1.plot(count['Year'], count['Count'], color = "darkblue", label = "Volume Count")
ax1.legend(loc = "upper right")
ax1.set_xlabel('Year')
ax1.set_yticks([0,25000, 50000, 75000])
ax1.set_yticklabels(["0", "25,000", "50,000", "75,000"])
plt.ylim([0,75000])
fig.savefig('../output/volumes_over_time/total_volumes.png', dpi = 200)

#Ternary plots

if half_century is True:
    years = []
    for year in range(1550, 1891, 50):
        years.append(year)

def ternary_plots(data, color, path, legend_title, years = years, grayscale = False, size = None, decreasing_scale = False):
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
                        coloraxis_colorbar_title_text = legend_title,
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

        # if year == 1850:   
        #     fig.write_image(path + str(year) + '.png', width=900) #included because wider format needed for color scale
        
        # else:
        #     fig.update(layout_coloraxis_showscale=False) #removes colorbar
        #     fig.write_image(path + str(year) + '.png') #only works with kaleido 0.1.0 for some reason, use 'conda install python-kaleido=0.1.0post1' on PC, also uses plotly 5.10.0
        
        # Uncomment for no legend at all
        fig.update(layout_coloraxis_showscale=False) #removes colorbar
        fig.write_image(path + str(year) + '.png') #only works with kaleido 0.1.0 for some reason, use 'conda install python-kaleido=0.1.0post1' on PC, also uses plotly 5.10.0


print('Progress Triangles, color')
ternary_plots(data = moving_volumes,
              color = 'progress_percentile',
              legend_title='Progress (Percentile)',
              path = '../output/volume_triangles/progress/color/')

print('Progress Triangles, grayscale')
ternary_plots(data = moving_volumes,
              color = 'progress_percentile',
              legend_title='Progress (Percentile)',
              path = '../output/volume_triangles/progress/grayscale/',
              grayscale=True)

print('Optimistic Triangles, color')
ternary_plots(data = moving_volumes,
              color = 'optimistic_percentile',
              legend_title='Optimistic (Percentile)',
              path = '../output/volume_triangles/optimistic/')

print('Industry Triangles, color')
ternary_plots(data = moving_volumes,
              color = 'industry_3_percentile',
              legend_title='Industry (Percentile)',
              path = '../output/volume_triangles/industry/color/')

print('Industry Triangles, grayscale')
ternary_plots(data = moving_volumes,
              color = 'industry_3_percentile',
              legend_title='Industry (Percentile)',
              path = '../output/volume_triangles/industry/grayscale/',
              grayscale=True)

print('Size based, increasing')
ternary_plots(data = moving_volumes,
              color = 'progress_percentile',
              size = 'industry_3_percentile',
              legend_title='Progress (Percentile)',
              path = '../output/volume_triangles/industry_optimism/increasing_scale/')

print('Size based, decreasing')
ternary_plots(data = moving_volumes,
              color = 'progress_percentile',
              size = 'industry_3_percentile',
              legend_title='Progress (Percentile)',
              decreasing_scale=True,
              path = '../output/volume_triangles/industry_optimism/decreasing_scale/')



print('Progress minus regression')
ternary_plots(data=moving_volumes,
              color='progress_regression_percentile',
              legend_title='Progress - Regression (Percentile)',
              path = '../output/volume_triangles/progress_regression/')
 

