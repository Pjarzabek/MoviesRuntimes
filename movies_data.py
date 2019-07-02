import pandas as pd
import math

# Download data from IMDB website
# Data description https://www.imdb.com/interfaces/
movies = pd.read_csv('https://datasets.imdbws.com/title.basics.tsv.gz', compression='gzip', sep='\t')
print('"title.basics.tsv.gz" downloaded')
ratings = pd.read_csv('https://datasets.imdbws.com/title.ratings.tsv.gz', compression='gzip', sep='\t')
print('"title.ratings.tsv.gz" downloaded')
print(movies.shape)
print(ratings.shape)

# Merge data on 'tconst', which is unique id for any title in IMDB database.
movies = pd.merge(movies, ratings, on='tconst')
print(movies.shape)
# In total there is almost 950k unique titles.

# Check titleType column.
print(movies['titleType'].unique())
# There are 11 types of titles, including TV shows, TV shows episodes, shorts and video games.
# We are interested only in movies.
movies = movies[movies['titleType'].isin(['movie'])]  # , 'tvMovie'
print(movies.shape)
# The number of titles dropped significantly to 235k.
# Let's check movie genres
genres = movies['genres'].unique()
print(len(genres))

# We are not interested in documentaries, because they can skew our results.
# Let's drop them.
movies = movies[movies['genres'].str.contains('Documentary') == False]

# Now we can remove all unnecessary columns. We only need year of release, runtime and number of votes (popularity).
movies = movies[['startYear', 'runtimeMinutes', 'numVotes']]

# Change data type to numeric and drop NA values
for column in movies.columns.values.tolist():
    movies[column] = pd.to_numeric(movies[column], errors='coerce')

movies = movies.dropna()
print(movies.shape)
# Number of movies dropped to 177k.
# Descriptive statistics
print(movies.describe())

# Some movies are 1 minute long, which is probably a mistake.
# According to the Academy of Motion Picture Arts and Sciences, an original film needs
# to be less than 40 minutes to qualify as a short film, whereas a feature film is more than 40 minutes.
# This is why we will drop any movie which is 40 minutes long or less.

movies = movies[movies['runtimeMinutes'] > 40]

# What’s more important, we are only interested in popular movies. There are thousands of movies in IMDb database
# which have only a few dozen votes. They can skew our results.
# Let’s say we will use 20% of most movies which got the most votes in every year.

popular_movies = pd.DataFrame()
for year in range(1894, 2020):
    movies_year = movies[movies['startYear'] == year].sort_values(by=['numVotes'], ascending=False)
    if len(movies_year) > 10:  # Quick filter to eliminate experimental years of cinema
        num_of_movies = math.floor(0.2 * len(movies_year))
        twenty_percent = movies_year.iloc[0:num_of_movies]  # subset of 20% of most popular movies
        popular_movies = popular_movies.append(twenty_percent)

movies = popular_movies
print(movies.describe())
# After filtering there are 35531 movies in our dataset
# Save data to CSV
popular_movies.to_csv('movies.csv', index=False)
print('movies.csv created successfully!')

# The rest of data exploration will be done in movies.py file. The purpose of this
# script is to reduce amount of time needed for calculations when rerunning.
# Also, there is no need to download data again every time when the script will be run.
# The size of the dataset is reduced by over 99%. Deleted data was irrelevant in our study.
