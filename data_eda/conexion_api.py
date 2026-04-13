
import requests
import pandas as pd

#API Key
API_KEY = "903d94755233e0bd7a4a04e0de529bab"

#URL de TMDB (películas)
url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=es-ES"

response = requests.get(url)
data = response.json()

movies = data["results"]
df = pd.DataFrame(movies)

df = df[["title", "vote_average", "overview", "genre_ids"]]

#Traer géneros

url_genres = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=es-ES"
response_genres = requests.get(url_genres)
data_genres = response_genres.json()

#Crear diccionario id → nombre
genre_dict = {g["id"]: g["name"] for g in data_genres["genres"]}

#NUEVO: mapear géneros

df["genres"] = df["genre_ids"].apply(lambda ids: [genre_dict[i] for i in ids])

# df = df.drop(columns=["genre_ids"])

#Ver primeras filas
print(df.head())

#Guardar CSV
df.to_csv("peliculas.csv", index=False)