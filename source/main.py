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
    "amor": 10749,

    "terror": 27,
    "miedo": 27,
    "horror": 27,

    "drama": 18,
    "dramática": 18
}

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

        if incluir_actor:
            actor_incluir_id = recomendador.buscar_actor(incluir_actor)

        if excluir_actor:
            actor_excluir_id = recomendador.buscar_actor(excluir_actor)

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
            continue   # 🔥 vuelve a preguntar automáticamente

        # ========================
        # PROCESAR
        # ========================

        if data and data["results"]:
            data_genres = recomendador.obtener_generos()
            df = recomendador.crear_dataframe(data)
            df = recomendador.mapear_generos(df, data_genres)
            df = recomendador.limpiar_y_ordenar(df)

            print("\n🎬 Te recomiendo:\n")

            for _, row in df.head(5).iterrows():
                titulo = row["title"] if row["title"] else row["original_title"]
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
                break   # vuelve al inicio del while principal

            elif seguir == "no":
                print("👋 ¡Hasta luego!")
                return  # termina el programa

            else:
                print("Por favor respondé 'si' o 'no'")