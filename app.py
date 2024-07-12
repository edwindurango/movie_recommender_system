import pickle
import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

def fetch_genre(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    genres = [genre['name'] for genre in data['genres']]
    return ', '.join(genres)

def recommend(movie, movies, similarity, user_history):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommend_movie_names = []
    recommend_movie_posters = []
    recommend_movie_genres = []

    for i in distances[1:]:
        movie_id = movies.iloc[i[0]]['movie_id']
        movie_title = movies.iloc[i[0]]['title']
        if movie_title not in user_history:
            recommend_movie_posters.append(fetch_poster(movie_id))
            recommend_movie_names.append(movie_title)
            recommend_movie_genres.append(fetch_genre(movie_id))
            if len(recommend_movie_names) >= 10:
                break

    return recommend_movie_names, recommend_movie_posters, recommend_movie_genres

# Inicializar el historial de películas vistas en session_state
if 'movies_seen' not in st.session_state:
    st.session_state['movies_seen'] = []

if 'num_recommendations' not in st.session_state:
    st.session_state['num_recommendations'] = 3

st.sidebar.header("CineBot: Tu Guía Instantánea de Películas")
st.sidebar.image('https://img.blogs.es/iahuawei/wp-content/uploads/2018/12/mitos-1080x675.jpg')
st.sidebar.write('Experimenta la magia de la recomendación de películas en tiempo real')

st.header('Sistema de Recomendación')

# Cargar los datos
movies = pd.read_pickle('C:/Users/cafelio/Desktop/proyecto_peliculas/model/movies_list.pkl')
similarity = pd.read_pickle('C:/Users/cafelio/Desktop/proyecto_peliculas/model/similarity.pkl')

# Interfaz de selección de película
movie_list = movies['title'].values
selected_movie = st.selectbox("Selecciona una película de la lista para obtener recomendaciones", movie_list)

# Botón para mostrar recomendaciones
if st.button('Mostrar Recomendaciones'):
    recommend_movie_names, recommend_movie_posters, recommend_movie_genres = recommend(selected_movie, movies, similarity, st.session_state['movies_seen'])
    st.session_state['recommend_movie_names'] = recommend_movie_names
    st.session_state['recommend_movie_posters'] = recommend_movie_posters
    st.session_state['recommend_movie_genres'] = recommend_movie_genres
    st.session_state['num_recommendations'] = 3

# Mostrar recomendaciones
if 'recommend_movie_names' in st.session_state:
    recommend_movie_names = st.session_state['recommend_movie_names']
    recommend_movie_posters = st.session_state['recommend_movie_posters']
    recommend_movie_genres = st.session_state['recommend_movie_genres']
    num_recommendations = st.session_state['num_recommendations']

    cols = st.columns(3)
    for i in range(num_recommendations):
        if i < len(recommend_movie_names):
            col = cols[i % 3]
            col.text(recommend_movie_names[i])
            col.image(recommend_movie_posters[i])
            col.text(recommend_movie_genres[i])

    if num_recommendations < len(recommend_movie_names):
        if st.button('Mostrar más recomendaciones'):
            st.session_state['num_recommendations'] += 3
            st.experimental_rerun()