import streamlit as st
import recomendador
from nlp_spacy import interpretar_actores
import requests
from conexion_api import API_KEY

st.set_page_config(page_title="Recomendador de Películas", layout="centered")

st.title("🎬 Recomendador de Películas")
st.write("¿Qué te gustaría ver hoy? 🍿")

# ========================
# 🔥 FUNCIONES
# ========================

def reset_busqueda():
    st.session_state.busqueda_realizada = False
    st.session_state.query = ""

# ========================
# 🔥 SESSION STATE
# ========================

if "busqueda_realizada" not in st.session_state:
    st.session_state.busqueda_realizada = False

if "query" not in st.session_state:
    st.session_state.query = ""

# ========================
# INPUT
# ========================

user_input = st.text_input(" ", key="query")

# ========================
# BOTÓN BUSCAR
# ========================

if st.button("Buscar"):
    st.session_state.busqueda_realizada = True

# ========================
# LÓGICA PRINCIPAL
# ========================

if st.session_state.busqueda_realizada:

    if not user_input:
        st.warning("Por favor escribí algo 😅")
        st.stop()

    user_input = user_input.lower()

    # ========================
    # 🎯 DETECCIÓN DE GÉNERO
    # ========================

    mapa_generos = {
        "accion": 28, "acción": 28, "peleas": 28, "explosiones": 28,
        "comedia": 35, "divertido": 35, "divertida": 35, "graciosa": 35, "gracioso": 35, "humor": 35, "risa": 35,
        "triste": 18, "drama": 18, "dramática": 18, "emocional": 18,
        "romance": 10749, "romántica": 10749, "romantica": 10749, "amor": 10749,
        "terror": 27, "miedo": 27, "horror": 27, "susto": 27
    }

    generos_nombres = {
        28: "acción",
        35: "comedia",
        18: "drama",
        10749: "romance",
        27: "terror"
    }

    genero_detectado = None

    for palabra, genero_id in mapa_generos.items():
        if palabra in user_input:
            genero_detectado = genero_id

    # ========================
    # 🎭 NLP ACTORES
    # ========================

    actor_incluir_id = None
    actor_excluir_id = None

    incluir_actor, excluir_actor = interpretar_actores(user_input)

    if incluir_actor:
        actor_incluir_id = recomendador.buscar_actor(incluir_actor)
        if not actor_incluir_id:
            incluir_actor = None

    if excluir_actor:
        actor_excluir_id = recomendador.buscar_actor(excluir_actor)
        if not actor_excluir_id:
            excluir_actor = None

    # ========================
    # CONSULTA API
    # ========================

    data = None

    if genero_detectado and actor_incluir_id:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genero_detectado}&with_cast={actor_incluir_id}&language=es-ES"
        data = requests.get(url).json()

    elif genero_detectado:
        data = recomendador.obtener_peliculas_por_genero(genero_detectado)

    elif actor_incluir_id:
        data = recomendador.peliculas_por_actor(actor_incluir_id)

    else:
        st.error("Hmm… no terminé de entender 😅 ¿podés intentar de otra forma?")
        st.stop()

    # ========================
    # PROCESAMIENTO
    # ========================

    if data and "results" in data and len(data["results"]) > 0:

        df = recomendador.crear_dataframe(data)
        df = recomendador.limpiar_y_ordenar(df)

        # 🔥 CACHE CAST
        cache_cast = {}

        def obtener_cast(movie_id):
            if movie_id not in cache_cast:
                cache_cast[movie_id] = recomendador.obtener_cast_pelicula(movie_id)
            return cache_cast[movie_id]

        # 🔥 FILTROS
        df = df[df["id"].apply(
            lambda movie_id: (
                (actor_incluir_id in obtener_cast(movie_id) if actor_incluir_id else True)
                and
                (actor_excluir_id not in obtener_cast(movie_id) if actor_excluir_id else True)
            )
        )]

        # ========================
        # 🧠 MENSAJE INTELIGENTE
        # ========================

        mensaje = "😎 Tengo justo lo que buscás, mirá esto:"

        if genero_detectado and actor_incluir_id and actor_excluir_id:
            genero_nombre = generos_nombres.get(genero_detectado, "")
            mensaje = f"😎 {genero_nombre.capitalize()} con {incluir_actor.title()} pero sin {excluir_actor.title()} 👀"

        elif genero_detectado and actor_incluir_id:
            genero_nombre = generos_nombres.get(genero_detectado, "")
            mensaje = f"😎 {genero_nombre.capitalize()} con {incluir_actor.title()}, mirá esto:"

        elif actor_incluir_id and actor_excluir_id:
            mensaje = f"😎 Te tengo algo de {incluir_actor.title()} pero sin {excluir_actor.title()} 👀"

        elif actor_incluir_id:
            mensaje = f"😎 Películas de {incluir_actor.title()}, mirá esto:"

        elif genero_detectado:
            genero_nombre = generos_nombres.get(genero_detectado, "")
            mensaje = f"😎 Buscabas algo de {genero_nombre}, mirá esto:"

        # ========================
        # RESULTADOS
        # ========================

        if df.empty:
            st.warning("😅 No encontré resultados con esos filtros")
        else:
            st.subheader(mensaje)

            for _, row in df.head(5).iterrows():
                titulo = row["title"] or row["original_title"]
                titulo_original = row["original_title"]
                anio = row["release_date"][:4] if row["release_date"] else "N/A"

                st.markdown(f"### 🎬 {titulo} ({anio})")

                if titulo != titulo_original:
                    st.markdown(f"*({titulo_original})*")

                st.write(f"⭐ {row['vote_average']}/10")
                st.write(row["overview"])
                st.divider()

    else:
        st.error("No encontré resultados 😅")

    # ========================
    # BOTÓN RESET
    # ========================

    st.button("🔄 Nueva búsqueda", on_click=reset_busqueda)