import pandas as pd, \
    matplotlib.pyplot as plt, \
    matplotlib.patches as mpatches, \
    matplotlib.lines as mlines, \
    seaborn as sns

# Base dataset was created in movies_data.py file.
# In this script we continue data processing and make data visualization
movies = pd.read_csv('movies.csv')
print(movies.describe())

# Let's take a look at years distribution.
# There is a possibility that the number of movies in the beginning of cinematography
# will be to small to use in the report.
# Let's plot a histogram of movies older than 1940.

plt.hist(movies['startYear'][movies['startYear'] < 1940])
plt.title('Movies count')
plt.xlabel('Year of release')
plt.ylabel('Number of movies')
plt.show()

# We need to take a closer look at the early years.

plt.hist(movies['startYear'][movies['startYear'] < 1930])
plt.title('Movies count')
plt.xlabel('Year of release')
plt.ylabel('Number of movies')
plt.show()

# Ok, we can see that there are only few movies from early years of cinema,
# which have enough votes.
# Table should give better picture.
print(movies['startYear'][movies['startYear'] < 1940].value_counts().sort_index())

# We should get rid of years when there were only few movies. Let's take the same rule of thumb as with popular
# normal distribution approach. It defines minimum sample size as 30 elements. Let's calculate the start year of our data.

start_year = 0  # This will be starting year of the data.
# Create data frame with year as first column and movie count as second.
movies_per_year = movies['startYear'].value_counts().sort_index()  # The year is an index, we need it as a column.
movies_per_year_df = pd.DataFrame({'year': movies_per_year.index, 'movie_count': movies_per_year.values})

for i in range(0, len(movies_per_year_df)):
    year = movies_per_year_df.iloc[i, 0]
    movie_count = movies_per_year_df.iloc[i, 1]
    # Check if in a given year there were more than 30 movies.
    if movie_count > 30:
        movies_per_year_df = movies_per_year_df.iloc[i:, :]  # Drop years before current one in the loop
        # Check whether the rest of years have movie count above 30, if not, the loop continues.
        # If every year left has movie count above 30, the loop breaks and we have the answer.
        if sum(movies_per_year_df['movie_count'] < 30) == 0:
            start_year = year
            break

print(start_year)
# The dataset will start from the year 1931. Of course it was easy to see it by inspecting value counts table,
# but the goal was to practice loops and conditions to automate the process.

movies = movies[movies['startYear'] >= 1931]
print(movies.describe())

# Our final data is 27743 movies starting from year 1931 until 2018.
# Now let's plot distribution of movie lengths. We limited it to 40-200 minutes range to improve readability.
# There are not many movies longer than 200 minutes and 40 is lower limit of our data.
# Every bin corresponds to 10 minute range.
plt.hist(movies['runtimeMinutes'], range=(40, 200), bins=16, ec='black')
plt.title('Movies length')
plt.xlabel('Minutes')
plt.ylabel('Number of movies')
plt.show()
# The most popular runtime is 90-100 minute. Vast majority of movies is 80-120 minutes long.
# This is consistent with our movie-watching intuition.

# Let's find average movie runtime by year
# We group dataset by year and get descriptive statistics of every subset.
statistics_grouped = movies['runtimeMinutes'].groupby(movies['startYear']).describe()

# Data for the plot
avg_runtime_by_year = statistics_grouped['mean']  # Mean
avg_runtime_lower_band = statistics_grouped['mean'] - statistics_grouped['std']  # Lower band of data created using standard deviation.
avg_runtime_upper_band = statistics_grouped['mean'] + statistics_grouped['std']  # Upper band of data.

# Plot
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(avg_runtime_by_year, color="blue")
ax1.plot(avg_runtime_lower_band, color="aqua")
ax1.plot(avg_runtime_upper_band, color="aqua")
ax1.fill_between(statistics_grouped.index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')  # Fill space between bands to create confidence interval.
ax1.set_title('Movies runtime by year')
ax1.set_ylabel('Minutes')
ax1.set_xlabel('Release year')
ax1.set_xlim(1931, 2018)
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation')  # Used mpatches to create rectangular for a legend.
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
ax1.legend(handles=[legend_line, legend_sd])  # Nice legend with rectangular and line.
plt.show()

# The plot shows that movies were getting longer until year 1960.
# The average runtime increased in that time from ~90 minutes to ~105 minute.
# Since then there is no visible trend on the chart.

# What proportion of movies was taken into account?
# Let's calculate everything in the confidence interval

# Data for additional plot
percentage_of_included_movies = []
for year in statistics_grouped.index:
    movies_from_year = movies[movies['startYear'] == year]
    avg_runtime_low = avg_runtime_lower_band[int(year)]
    avg_runtime_up = avg_runtime_upper_band[int(year)]
    movies_included = movies_from_year[movies_from_year['runtimeMinutes'] > avg_runtime_low][movies_from_year['runtimeMinutes'] < avg_runtime_up]
    percentage_of_included_movies.append(len(movies_included)/len(movies_from_year))

statistics_grouped['included_movies_perc'] = percentage_of_included_movies
print(statistics_grouped['included_movies_perc'].describe())
# On average 78% of the popular movies were taken into account when creating the chart above.

# We can create a new chart with added plot for proportions

# Main plot
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(avg_runtime_by_year, color="blue")
ax1.plot(avg_runtime_lower_band, color="aqua")
ax1.plot(avg_runtime_upper_band, color="aqua")
ax1.fill_between(statistics_grouped.index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')
ax1.set_title('Movies runtime by year')
ax1.set_ylabel('Minutes')
ax1.set_xlabel('Release year')
ax1.set_xlim(1931, 2018)
# Plot with proportions
ax2 = ax1.twinx()
ax2.plot(statistics_grouped['included_movies_perc'], color='olive')
ax2.set_ylabel('Proportion')
plt.axhline(y=0.70, color='red', linestyle='dashed')  # Add line at 0.70
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation')
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
legend_line_2 = mlines.Line2D([], [], color='olive', label='Proportion included in CI')
dashed_line = mlines.Line2D([], [], color='red', label='Proportion = 0.7', linestyle='dashed')
ax1.legend(handles=[legend_line, legend_sd, legend_line_2, dashed_line])
plt.show()

# After 1950 all the time over 70% of popular movies were in the confidence interval area.
# Let's see what will happen if we take a look at 50% of most popular movies using quartile data and the median.

# Data
avg_runtime_by_year = statistics_grouped['50%']
avg_runtime_lower_band = statistics_grouped['25%']
avg_runtime_upper_band = statistics_grouped['75%']


# Plot
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(avg_runtime_by_year, color="blue")
ax1.plot(avg_runtime_lower_band, color="aqua")
ax1.plot(avg_runtime_upper_band, color="aqua")
ax1.fill_between(statistics_grouped.index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')
ax1.set_title('Movies runtime by year')
ax1.set_ylabel('Minutes')
ax1.set_xlabel('Release year')
ax1.set_xlim(1931, 2018)
legend_sd = mpatches.Patch(color='aqua', label='Interquartile range')
legend_line = mlines.Line2D([], [], color='blue', label='Median runtime')
ax1.legend(handles=[legend_line, legend_sd])
plt.show()

# Still, there is no sign of movies getting longer, especially after 1960. Maybe the problem is that we
# take into account too much movies from every year.
# There is a possibility that only the most popular movies are getting longer. Let's take a look at movies from 1960
# and newer (when uptrend stopped) and take into account only 50 most popular movies from every year.

movies_since_1960 = movies[movies['startYear'] >= 1960]
# Function to return statistics about n most popular movies from every year (will be reused later)
def top_n_movies(data, n):
    top_n_movies_per_year = data.groupby('startYear').head(n)
    stats = top_n_movies_per_year['runtimeMinutes'].groupby(
        top_n_movies_per_year['startYear']).describe()
    return stats

# Let's find average movie runtime by year, but consider only 50 most popular movies from every year.
statistics_grouped_50 = top_n_movies(movies_since_1960, 50)
# Data
avg_runtime_by_year = statistics_grouped_50['mean']
avg_runtime_lower_band = statistics_grouped_50['mean'] - statistics_grouped_50['std']
avg_runtime_upper_band = statistics_grouped_50['mean'] + statistics_grouped_50['std']

# Plot
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(avg_runtime_by_year, color="blue")
ax1.plot(avg_runtime_lower_band, color="aqua")
ax1.plot(avg_runtime_upper_band, color="aqua")
ax1.fill_between(statistics_grouped_50.index, avg_runtime_lower_band, avg_runtime_upper_band, facecolor='aqua')
ax1.set_title('Runtime of 50 most popular movies by year')
ax1.set_ylabel('Minutes')
ax1.set_xlabel('Release year')
ax1.set_xlim(1960, 2018)
legend_sd = mpatches.Patch(color='aqua', label='Mean +/- standard deviation')
legend_line = mlines.Line2D([], [], color='blue', label='Mean runtime')
ax1.legend(handles=[legend_line, legend_sd])
plt.show()

# Still no visible trend.

# Let's check different number of most popular movies.
# This time we will only take a look at average runtime.
# We can use 'top_n_movies' function created earlier.
mean_10 = top_n_movies(movies_since_1960, 10)['mean']
mean_30 = top_n_movies(movies_since_1960, 30)['mean']
mean_50 = top_n_movies(movies_since_1960, 50)['mean']
mean_100 = top_n_movies(movies_since_1960, 100)['mean']
mean_all = top_n_movies(movies_since_1960, len(movies_since_1960))['mean']

# Chart
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(mean_10, color='black')
ax.plot(mean_30, color='blue')
ax.plot(mean_50, color='red')
ax.plot(mean_100, color='green')
ax.plot(mean_all, color='purple')
ax.set_title('Movies runtime by year')
ax.set_ylabel('Minutes')
ax.set_xlabel('Release year')
ax.set_xlim(1960, 2018)
ax.legend(labels=['10 most popular movies',
                  '30 most popular movies',
                  '50 most popular movies',
                  '100 most popular movies',
                  'All popular movies'])
plt.show()

# No matter what number of most popular movies we take, there is no sign of trend.
# When we consider less movies from every year, there is more volatility on the chart,
# which is correct with our statistical intuition.
# To be sure that more popular movies are not longer, let's create a table with mean
# from all n-most popular movies of the year - mean of means
total_mean = pd.Series()
mean_list = [mean_10, mean_30, mean_50, mean_100, mean_all]
index_list = ['top_10', 'top_30', 'top_50', 'top_100', 'all']
for i in range(0, 5):
    mean_n = pd.Series([mean_list[i].mean()], index=[index_list[i]])
    total_mean = total_mean.append(mean_n)

print(total_mean)

# As you can see in the table, no matter how many most popular movies we consider,
# there is not much difference between average runtimes.
# In case of 10 most popular movies from every year average runtime is even shorter,
# but it is probably because of really small sample.

# Let's create boxplot for every decade.
movies_by_decade = movies.copy()
movies_by_decade['startYear'] = ((movies_by_decade['startYear'] // 10) * 10).astype('int64')
sns.boxplot(x="startYear", y="runtimeMinutes", data=movies_by_decade, color='lightskyblue', showfliers=False)
plt.ylim(40,180)
plt.title('Movies runtime by decade')
plt.xlabel('Decade')
plt.ylabel('Minutes')
plt.show()

# Since 1960' movies are not getting any longer.
# What's more, any difference noted during this study is too small to be noticed
# by the audience. It means that the movies are not getting longer in time,
# it is just popular illusion among moviegoers.