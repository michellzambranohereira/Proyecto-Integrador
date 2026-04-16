from conexion_api import *
from nlp_spacy import interpretar_actores
import recomendador
import requests

mapa_generos = {
    "accion": 28,
    "acción": 28,
    "peleas": 28,
    "explosiones": 28,

    "comedia": 35,
    "graciosa": 35,
    "divertida": 35,

    "romance": 10749,
    "romántica": 10749,
    "romantica": 10749,
    "amor": 10749,

    "terror": 27,
    "miedo": 27,
    "horror": 27,

    "drama": 18,
    "dramática": 18
}

def limpiar_texto_actor(texto):
    if not texto:
        return texto

    basura = ["que", "no", "esté", "este", "sea", "salga", "aparezca", "en"]
    palabras = texto.split()
    palabras_limpias = [p for p in palabras if p not in basura]

    return " ".join(palabras_limpias)


def main():
    while True:
        user_input = input("\n¿Qué querés ver? ").lower()

        genero_detectado = None
        actor_incluir_id = None
        actor_excluir_id = None

        # 🎯 detectar género
        for palabra, genero_id in mapa_generos.items():
            if palabra in user_input:
                genero_detectado = genero_id

        # 🎭 NLP actores
        incluir_actor, excluir_actor = interpretar_actores(user_input)

        # 🔥 FALLBACK INCLUIR
        if not incluir_actor:
            if "de" in user_input:
                incluir_actor = user_input.split("de")[-1].strip()
            else:
                palabras = user_input.split()
                if len(palabras) >= 2:
                    incluir_actor = " ".join(palabras[-2:])

        # 🔥 FALLBACK EXCLUIR
        if not excluir_actor:
            if "sin" in user_input:
                excluir_actor = user_input.split("sin")[-1].strip()
            elif "no" in user_input:
                excluir_actor = user_input.split("no")[-1].strip()

        # 🔥 LIMPIEZA CLAVE
        incluir_actor = limpiar_texto_actor(incluir_actor)
        excluir_actor = limpiar_texto_actor(excluir_actor)

        # 🔎 DEBUG (muy útil)
        #print("👉 incluir_actor:", incluir_actor)
        #print("👉 excluir_actor:", excluir_actor)

        # 🔎 BUSCAR IDS
        if incluir_actor:
            actor_incluir_id = recomendador.buscar_actor(incluir_actor)

        if excluir_actor:
            actor_excluir_id = recomendador.buscar_actor(excluir_actor)

        #print("👉 ID incluir:", actor_incluir_id)
        #print("👉 ID excluir:", actor_excluir_id)

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
            print("No entendí tu búsqueda 😅")
            continue

        # ========================
        # PROCESAR
        # ========================

        if data and "results" in data and len(data["results"]) > 0:
            data_genres = recomendador.obtener_generos()
            df = recomendador.crear_dataframe(data)
            df = recomendador.mapear_generos(df, data_genres)
            df = recomendador.limpiar_y_ordenar(df)

            # 🔥 CACHE DEL CAST (clave)
            cache_cast = {}

            def obtener_cast(movie_id):
                if movie_id not in cache_cast:
                    cache_cast[movie_id] = recomendador.obtener_cast_pelicula(movie_id)
                return cache_cast[movie_id]

            # 🔥 FILTRO CORRECTO
            df = df[df["id"].apply(
                lambda movie_id: (
                    (actor_incluir_id in obtener_cast(movie_id) if actor_incluir_id else True)
                    and
                    (actor_excluir_id not in obtener_cast(movie_id) if actor_excluir_id else True)
                )
            )]

            if df.empty:
                print("😅 No encontré resultados con esos filtros")
            else:
                print("\n🎬 Te recomiendo:\n")

                for _, row in df.head(5).iterrows():
                    titulo_es = row["title"]
                    titulo_original = row["original_title"]
                    if titulo_es != titulo_original:
                         titulo = f"{titulo_es} ({titulo_original})"
                    else:
                        titulo = titulo_es
                    anio = row["release_date"][:4] if row["release_date"] else "N/A"

                    print(f"""
🎬 {titulo} ({anio})
⭐ {row['vote_average']}/10
📖 {row['overview']}
""")
        else:
            print("No encontré resultados 😅")

        # ========================
        # CONTINUAR O SALIR
        # ========================

        while True:
            seguir = input("\n¿Querés hacer otra consulta? (si/no): ").lower()

            if seguir in ["si", "sí"]:
                break

            elif seguir == "no":
                print("👋 ¡Hasta luego!")
                return

            else:
                print("Por favor respondé 'si' o 'no'")


if __name__ == "__main__":
    main()