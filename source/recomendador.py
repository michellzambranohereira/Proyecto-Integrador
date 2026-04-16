
# Segunda etapa (prototipo): con la información obtenida de la API, creamos un prototipo recomendador de películas
import requests
import pandas as pd

API_KEY = "903d94755233e0bd7a4a04e0de529bab"

# ========================
# FUNCIONES API
# ========================

def obtener_peliculas_por_genero(genero_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genero_id}&language=es-ES"
    return requests.get(url).json()

def buscar_actor(nombre_actor):
    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={nombre_actor}"
    data = requests.get(url).json()

    if "results" in data and len(data["results"]) > 0:
        return data["results"][0]["id"]
    
    return None

def obtener_cast_pelicula(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    data = requests.get(url).json()

    if "cast" in data:
        return [actor["id"] for actor in data["cast"]]

    return []

def peliculas_por_actor(actor_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_cast={actor_id}&language=es-ES"
    return requests.get(url).json()

def obtener_generos():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=es-ES"
    return requests.get(url).json()

# ========================
# PROCESAMIENTO
# ========================

def crear_dataframe(data):
    df = pd.DataFrame(data["results"])
    columnas = ["id", "title", "original_title", "vote_average", "overview", "genre_ids", "release_date"]
    df = df[columnas]
    return df

def mapear_generos(df, data_genres):
    genre_dict = {g["id"]: g["name"] for g in data_genres["genres"]}
    df["genres"] = df["genre_ids"].apply(lambda ids: [genre_dict[i] for i in ids])
    return df

def limpiar_y_ordenar(df):
    df = df[df["overview"].notna() & (df["overview"] != "")]
    df = df.sort_values(by="vote_average", ascending=False)
    return df