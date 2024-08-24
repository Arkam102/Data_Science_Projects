import pickle
import streamlit as st
import requests
import gdown
from jinja2 import Template
import os

api_key = st.secrets["TMDB_API_KEY"]

# Google Drive File IDs
similarity_file_id = '1YZ7ElUf43aptn0kH87mwGSEbZ5MS1f4I'
movies_file_id = '1xlLQ6XgBlqrhNGpFNRrWcsbJ_1-Tm0NA'  # Replace with your Google Drive file ID for movies.pkl

similarity_output = 'similarity.pkl'
movies_output = 'movies.pkl'

# CSS content as a string
css_content = """
.header {
    text-align: center;
    font-family: 'Alegreya', sans-serif;
    color: #1f77b4;
    font-size: 40px;
    margin-bottom: 20px;
}
.movie-container {
    display: flex;
    text-align: center;
    margin: 20px;
    height: max-content;
    width: fit-content;
    flex-wrap: wrap;
}
.movie-title {
    flex-wrap: wrap;
    font-size: 20px;
    font-weight: bold;
    color: rgb(4, 124, 4);
    margin-top: 10px;
}
.movie-rating {
    font-size: 16px;
    color: #f39c12;
}
.movie-poster {
    border-radius: 10px;
    width: 100px;
    height: 150px;
    cursor: pointer;
}
"""

# HTML template content as a string
html_template = """
<div class="movie-container">
    <a href="{{ imdb_url }}" target="_blank">
        <img src="{{ poster }}" class="movie-poster"/>
    </a>
    <div class="movie-title">{{ title }}</div>
    <div class="movie-rating">Rating: {{ rating }}</div>
</div>
"""

# Function to download files from Google Drive
def download_file_from_drive(file_id, output):
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, output, quiet=False)

# Function to fetch movie details
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
    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Function to render HTML template
def render_template(context):
    template = Template(html_template)
    return template.render(context)

# Download the files if they do not exist
if not os.path.exists(similarity_output):
    download_file_from_drive(similarity_file_id, similarity_output)

if not os.path.exists(movies_output):
    download_file_from_drive(movies_file_id, movies_output)

# Main code
st.markdown('<div class="header">Movie Recommender System</div>', unsafe_allow_html=True)
movies = pickle.load(open(movies_output, 'rb'))
similarity = pickle.load(open(similarity_output, 'rb'))

load_css()

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie to get similar recommendations:", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_details = recommend(selected_movie)
    cols = st.columns(5)
    for col, movie in zip(cols, recommended_movie_details):
        with col:
            html_content = render_template(movie)
            st.markdown(html_content, unsafe_allow_html=True)
