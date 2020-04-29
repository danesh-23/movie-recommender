import pandas as pd
from typing import List, Tuple


def preformat_movies(user_movies_file: str) -> Tuple:
    data_cols = ["user_id", "movie_id", "rating"]
    movies_liked = []
    with open(user_movies_file, "r") as file:
        for line in file.readlines():
            movies_liked.append(line.strip())

    data_mov = pd.read_csv("mv-100k/u.data", sep="\t", names=data_cols, usecols=range(3),
                           encoding="ISO-8859-1")
    data_info = pd.read_csv("mv-100k/u.item", delimiter="|",
                            names=["movie_id", "movie_title"], usecols=[0, 1], encoding="ISO-8859-1")

    movies = pd.merge(data_mov, data_info)

    movie_ratings_data = pd.pivot_table(movies, index=["user_id"], columns=["movie_title"], values="rating")

    corr_matrix = movie_ratings_data.corr(min_periods=250)
    # finds correlation but eliminates spurious results by removing pairs rated by <= 250 people
    return movies_liked, corr_matrix


def recommend_movies_to_user(movies_file: str) -> List:
    user_movies, corr_matrix = preformat_movies(movies_file)
    sim_candidates = pd.Series()
    for movies in user_movies:
        print("Finding similarities to {}...".format(movies))
        try:
            sim_movies_rated = corr_matrix[movies].dropna()
    #   finding movies that were rated similarly to the the users current movie from the corr_matrix which shows the similarities

            sim_movies_rated = sim_movies_rated.map(lambda x: x * 5 * 2)
            sim_candidates = sim_candidates.append(sim_movies_rated)
        except:
            print("Couldn't find movie with title: {}\n".format(movies))

    print("\nSorting...\n")
    sim_candidates = sim_candidates.groupby(sim_candidates.index).sum()
    sim_candidates.sort_values(ascending=False, inplace=True)
    for movies in user_movies:
        if movies in sim_candidates.index:
            sim_candidates = sim_candidates.drop(movies)

    for sim_movies in sim_candidates.keys():
        print("You may also like {}".format(sim_movies))
    print("\nThese are the list of 19th century movies we think you may like based on your movie list and past trends.")

    return list(sim_candidates.keys())


