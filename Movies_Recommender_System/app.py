import pickle
import streamlit as st
import requests
import gdown
from jinja2 import Template
import os

api_key = st.secrets["TMDB_API_KEY"]

similarity_file_id = '1YZ7ElUf43aptn0kH87mwGSEbZ5MS1f4I'
movies_file_id = '1xlLQ6XgBlqrhNGpFNRrWcsbJ_1-Tm0NA' 

similarity_output = 'similarity.pkl'
movies_output = 'movies.pkl'

def download_file_from_drive(file_id, output):
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


def load_css():
    css_file_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_file_path):
        with open(css_file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error("CSS file 'styles.css' not found.")


def render_template(context):
    html_file_path = os.path.join(os.path.dirname(__file__), "template.html")
    if os.path.exists(html_file_path):
        with open(html_file_path) as f:
            template = Template(f.read())
        return template.render(context)
    else:
        st.error("HTML template 'template.html' not found.")
        return ""


if not os.path.exists(similarity_output):
    download_file_from_drive(similarity_file_id, similarity_output)

if not os.path.exists(movies_output):
    download_file_from_drive(movies_file_id, movies_output)


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
