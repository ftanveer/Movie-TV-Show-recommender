import streamlit as st
import pickle
import requests
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('MY_API_KEY')

######## File Reading #########

movie_names_desc = pickle.load(open('movie_names_desc.pkl','rb'))

df_1 = pickle.load(open('df_1.pkl','rb'))
df_2_nlp = pickle.load(open('df_2_nlp.pkl','rb'))
df_3_nlp = pickle.load(open('df_3_nlp.pkl','rb'))

### Generating cosine similarities  #####

########################################################### TFIDF

tfidf = TfidfVectorizer()

#vectorize the processed text

#tfidf_matrix = tfidf.fit_transform(df_2_nlp["description"])


# Compute the cosine similarity matrix

@st.cache_data
def get_tfidf_matrix(_column):
    tfidf_matrix = tfidf.fit_transform(_column)
    cosine = linear_kernel(tfidf_matrix, tfidf_matrix)

    return cosine

cosine_sim_tfidf = get_tfidf_matrix(df_2_nlp["description"])

##################################################### COUNT VECTORIZER

count = CountVectorizer()
#count_matrix = count.fit_transform(df_3_nlp['genres_soup'])


@st.cache_data
def get_countvc_matrix(_column):
    count_matrix = count.fit_transform(_column)
    cosine_sim_matrix = cosine_similarity(count_matrix, count_matrix)

    return cosine_sim_matrix

cosine_sim_countvec = get_countvc_matrix(df_3_nlp['soup'])

#####################################################COMBINATION

hybrid_cosine = cosine_sim_tfidf + cosine_sim_countvec


##### Get Posters #########

def get_poster(imdb_id):
    try:
        url = f'https://api.themoviedb.org/3/find/{imdb_id}?api_key={API_KEY}&language=en-US&external_source=imdb_id'
        response = requests.get(url)
        data = response.json()
        movie = data["movie_results"][0]
        poster = movie["poster_path"]

        poster_url = f'https://image.tmdb.org/t/p/original/{poster}'
    except:
        poster_url = "No Image Available"

    #actual_poster = st.image(poster_url, width=200)
    return poster_url

######## Function to access df #########

def get_df_info(df,_column, _index):
    info = df[_column][_index]
    return info

######## Recommendation functions #########

def recommendation_engine(movie_title, cosine_similar):
    recommended_movies = []
    movie_desc_list = []
    imdb_ids = []
    streaming_platform_list = []
    cost_list = []
    imdb_score_list = []

    index = movie_names_desc[movie_names_desc['title'] == movie_title].index[0]

    similarity_score = pd.Series(cosine_similar[index]).sort_values(ascending=False)

    top_10_content = (similarity_score.iloc[1:11].index)

    ## if movie name is  duplicated then it exists in multiple streaming platforms, hence we need
    ## to drop a duplcate name and mention both streaming platforms. We also need to add another
    ##recommendation to make up for the duplicate

    movie_data = [(get_df_info(df_1,'title',i),get_df_info(df_1,'description',i),get_df_info(df_1,'imdb_id',i),get_df_info(df_1,'streaming_service',i),
                   get_df_info(df_1,'subscription_cost',i),get_df_info(df_1,'imdb_score',i)) for i in top_10_content]

    recommended_movies = [m[0] for m in movie_data]
    movie_desc_list = [m[1] for m in movie_data]
    imdb_ids = [m[2] for m in movie_data]
    streaming_platform_list = [m[3] for m in movie_data]
    cost_list = [m[4] for m in movie_data]
    imdb_score_list = [m[5] for m in movie_data]


    # for i in top_10_content:
    #     recommended_movies.append(list(df_1['title'])[i])
    #     movie_desc_list.append(list(df_1['description'])[i])
    #     imdb_ids.append(list(df_1['imdb_id'])[i])
    #     streaming_platform_list.append(list(df_1['streaming_service'])[i])
    #     cost_list.append(list(df_1['subscription_cost'])[i])


    recommended_dict = {'Movie Name': recommended_movies, "Plot": movie_desc_list,"imdb_id":  imdb_ids, "streaming_service":streaming_platform_list,
                        "subscription_cost": cost_list,"imdb_score": imdb_score_list}
    recommended_df = pd.DataFrame.from_dict(recommended_dict)
    recommended_df["posters"] = recommended_df["imdb_id"].apply(get_poster)

    # for recom in recommendations["imdb_id"].values:
    #     movie_poster = get_poster(recomm)
    #     st.image(movie_poster, width=200)
    return recommended_df








######## UX Design #########

background =  'background.jpeg'
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1585314062340-f1a5a7c9328d?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1887&q=80");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

st.markdown("<h1 style='text-align: center; color: orange;'>Movie Recommender System</h1>", unsafe_allow_html=True)

all_content_names =  movie_names_desc['title'].values

content = st.selectbox("Search for a Movie / TV Show", all_content_names)



################################################################# MAIN FUNCTION ##############


if st.button('Recommend'):
  recommendations = recommendation_engine(content,hybrid_cosine)
  st.markdown(
      f"<strong style='color: orange;font-size :22px'> You might also like </strong>",
      unsafe_allow_html=True,
  )

  for index, row in recommendations.iterrows():

      ###### Movie Name

      movie_name = row["Movie Name"]

      st.markdown(
          f"<h2 style='color: orange;'>  {movie_name} </h2>",
          unsafe_allow_html=True,
      )

      ###### Poster Images

      try:
          st.image(row["posters"], width = 200)
      except:
          st.write("No preview available")

      ###### Plot

      plot = row["Plot"]
      st.markdown(
          f"<strong style='color: orange;font-size :24px'> Plot: </strong> <p style='color: orange;'> {plot} </p>",
          unsafe_allow_html=True,
      )
     ########## IMDb Score
      imdb_score = row["imdb_score"]
      st.markdown(
          f"<strong style='color: orange; font-size :24px'> IMDb Score: </strong><p style='color: orange;'>  {imdb_score} </p>",
          unsafe_allow_html=True,
      )
      ###### Streaming Service
      streaming_platform = row["streaming_service"]
      st.markdown(
          f"<strong style='color: orange;font-size :24px'>  Where to watch: </strong><p style='color: orange;'> {streaming_platform} streaming service. </p>",
          unsafe_allow_html=True,
      )

      cost = row["subscription_cost"]
      st.markdown(
          f"<strong style='color: orange; font-size :24px'> Subscription Cost: </strong><p style='color: orange;'>  {cost} and up. </p>",
          unsafe_allow_html=True,
      )










######## Side bar widget #########

# page = 0

# def main():
#     st.sidebar.title("Navigation")
#     global page
#     page = st.sidebar.radio("Choose a page", [0,1,2])
#
#     if page == 0:
#         st.write("You are on page 0")
#     elif page == 1:
#         st.write("You are on page 1")
#     elif page == 2:
#         st.write("You are on page 2")
# if __name__  == '__main__':
#     main()

