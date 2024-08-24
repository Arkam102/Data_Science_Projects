import pickle
import streamlit as st
import requests
import gdown
from jinja2 import Template
import os

api_key = st.secrets["TMDB_API_KEY"]

# Google Drive File ID for similarity.pkl
file_id = '1YZ7ElUf43aptn0kH87mwGSEbZ5MS1f4I'
output = 'similarity.pkl'

# Function to fetch movie details
def download_similarity_file():
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, output, quiet=False)
def fetch_movie_details(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    imdb_rating = data.get('vote_average', 'N/A')
    imdb_id = data.get('imdb_id', '')
    imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else '#'
    return full_path, imdb_rating, data.get('title', 'No title available'), imdb_url

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_details = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        poster, rating, title, imdb_url = fetch_movie_details(movie_id)
        recommended_movie_details.append({
            'title': title,
            'poster': poster,
            'rating': rating,
            'imdb_url': imdb_url
        })
    return recommended_movie_details

# Function to load CSS
def load_css():
    with open("D:/Projects/Movie_Recommender/movie_rec_system/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to render HTML template
def render_template(context):
    with open("D:/Projects/Movie_Recommender/movie_rec_system/template.html") as f:
        template = Template(f.read())
    return template.render(context)

if not os.path.exists(output):
    download_similarity_file()

# Main code
st.markdown('<div class="header">Movie Recommender System</div>', unsafe_allow_html=True)
movies = pickle.load(open('D:\Projects\Movie_Recommender\movie_rec_system\movies.pkl', 'rb'))
similarity = pickle.load(open(output, 'rb'))

load_css()

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie to get similar recommendations :", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_details = recommend(selected_movie)
    cols = st.columns(5)
    for col, movie in zip(cols, recommended_movie_details):
        with col:
            html_content = render_template(movie)
            st.markdown(html_content, unsafe_allow_html=True)
