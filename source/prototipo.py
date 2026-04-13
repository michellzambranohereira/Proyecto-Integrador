
# Segunda etapa (prototipo): con la información obtenida de la API, creamos un prototipo recomendador de películas
import requests
import pandas as pd

# ========================
# CONFIG
# ========================
API_KEY = "903d94755233e0bd7a4a04e0de529bab"

# ========================
# FUNCIONES API
# ========================

def obtener_peliculas_por_genero(genero_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genero_id}&language=es-ES"
    return requests.get(url).json()

def buscar_actor(nombre_actor):
    url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={nombre_actor}"
    response = requests.get(url)
    data = response.json()

    # 👇 DEBUG (opcional pero útil)
    #print(data)

    # 👇 validación segura
    if "results" in data and len(data["results"]) > 0:
        return data["results"][0]["id"]
    
    return None

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
    columnas = ["title", "original_title", "vote_average", "overview", "genre_ids", "release_date"]
    df = df[columnas]
    return df

def mapear_generos(df, data_genres):
    genre_dict = {g["id"]: g["name"] for g in data_genres["genres"]}
    df["genres"] = df["genre_ids"].apply(lambda ids: [genre_dict[i] for i in ids])
    return df

# ========================
# LÓGICA
# ========================

mapa_generos = {
    "accion": 28,
    "comedia": 35,
    "romance": 10749,
    "terror": 27,
    "drama": 18
}

# ========================
# MAIN
# ========================

user_input = input("¿Qué querés ver? ").lower()

genero_detectado = None
actor_detectado = None

# 🎯 detectar género
for palabra, genero_id in mapa_generos.items():
    if palabra in user_input:
        genero_detectado = genero_id

# 🎭 detectar actor (últimas dos palabras)
palabras = user_input.split()
if len(palabras) >= 2:
    nombre_actor = " ".join(palabras[-2:])
    actor_id = buscar_actor(nombre_actor)
    if actor_id:
        actor_detectado = actor_id

# ========================
# CONSULTA API
# ========================

data = None

# 🔥 combinación
if genero_detectado and actor_detectado:
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genero_detectado}&with_cast={actor_detectado}&language=es-ES"
    data = requests.get(url).json()

# 🎬 solo género
elif genero_detectado:
    data = obtener_peliculas_por_genero(genero_detectado)

# 🎭 solo actor
elif actor_detectado:
    data = peliculas_por_actor(actor_detectado)

else:
    print("No entendí tu búsqueda 😅")

# ========================
# PROCESAR Y MOSTRAR
# ========================

if data and data["results"]:
    
    data_genres = obtener_generos()
    df = crear_dataframe(data)
    df = mapear_generos(df, data_genres)

    # limpiar resultados
    df = df[df["overview"].notna() & (df["overview"] != "")]
    df = df.sort_values(by="vote_average", ascending=False)

    print("\n🎬 Te recomiendo:\n")

    for _, row in df.head(5).iterrows():
        titulo = row["title"] if row["title"] else row["original_title"]
        anio = row["release_date"][:4] if row["release_date"] else "N/A"

        print(f"""
🎬 {titulo} ({anio})
⭐ {row['vote_average']}/10
📖 {row['overview']}
""")

# ⚠️ fallback si no hay resultados combinados
elif genero_detectado and actor_detectado:
    print("\n😅 No encontré películas con ambos criterios.")
    print("👉 Pero te dejo algunas del actor:\n")

    data = peliculas_por_actor(actor_detectado)

    data_genres = obtener_generos()
    df = crear_dataframe(data)
    df = mapear_generos(df, data_genres)

    for _, row in df.head(5).iterrows():
        print(f"🎬 {row['title']} - ⭐ {row['vote_average']}")