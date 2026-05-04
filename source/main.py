from conexion_api import *
from nlp_spacy import interpretar_actores
import recomendador
import requests

#Diccionario de palabras clave para detectar géneros

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
    "dramática": 18,

    "suspenso": 9648,
    "misterio": 9648,
    "detective": 9648,
    "investigacion": 9648,

    "thriller": 53,
    "tension": 53,
    "tenso": 53,
    "intriga": 53,

    "policial": 80,
    "crimen": 80,
    "asesinato": 80,
    "mafia": 80

}

# Limpieza de texto de actores

def limpiar_texto_actor(texto):
    if not texto:
        return texto

    basura = ["que", "no", "esté", "este", "sea", "salga", "aparezca", "en"]
    palabras = texto.split()
    palabras_limpias = [p for p in palabras if p not in basura]

    return " ".join(palabras_limpias)

# ========================
# FUNCIÓN PRINCIPAL
# ========================

def main():
    while True:
        user_input = input("\n¿Qué querés ver? ").lower()

        genero_detectado = None
        actor_incluir_id = None
        actor_excluir_id = None

        # 🎯 Detectar género
        for palabra, genero_id in mapa_generos.items():
            if palabra in user_input:
                genero_detectado = genero_id

        # 🎭 NLP actores
        incluir_actor, excluir_actor = interpretar_actores(user_input)

        # Fallback incluir
        if not incluir_actor:
            if "de" in user_input:
                incluir_actor = user_input.split("de")[-1].strip()
            else:
                palabras = user_input.split()
                if len(palabras) >= 2:
                    incluir_actor = " ".join(palabras[-2:])

        # Fallback excluir
        if not excluir_actor:
            if "sin" in user_input:
                excluir_actor = user_input.split("sin")[-1].strip()
            elif "no" in user_input:
                excluir_actor = user_input.split("no")[-1].strip()

        # Limpieza
        incluir_actor = limpiar_texto_actor(incluir_actor)
        excluir_actor = limpiar_texto_actor(excluir_actor)

        # IDs
        if incluir_actor:
            actor_incluir_id = recomendador.buscar_actor(incluir_actor)

        if excluir_actor:
            actor_excluir_id = recomendador.buscar_actor(excluir_actor)

        # ========================
        # CONSULTA API
        # ========================

        data = None

        if genero_detectado and actor_incluir_id:
            # 🔥 CAMBIO: usar actor como base (más confiable)
            data = recomendador.peliculas_por_actor(actor_incluir_id)

        elif genero_detectado:
            data = recomendador.obtener_peliculas_por_genero(genero_detectado)

        elif actor_incluir_id:
            data = recomendador.peliculas_por_actor(actor_incluir_id)

        else:
            print("No entendí tu búsqueda 😅")
            continue

        # 🔥 NORMALIZAR RESPUESTA (clave)
        if data and "cast" in data:
            data = {"results": data["cast"]}

        # ========================
        # PROCESAMIENTO
        # ========================

        if data and "results" in data and len(data["results"]) > 0:

            print("👉 ENTRE AL BLOQUE DE RESULTADOS")

            data_genres = recomendador.obtener_generos()
            df = recomendador.crear_dataframe(data)
            df = recomendador.mapear_generos(df, data_genres)
            df = recomendador.limpiar_y_ordenar(df)

            print("Cantidad total ANTES de filtros:", len(df))

            # 🔥 CACHE CAST
            cache_cast = {}

            def obtener_cast(movie_id):
                if movie_id not in cache_cast:
                    cache_cast[movie_id] = recomendador.obtener_cast_pelicula(movie_id)
                return cache_cast[movie_id]

            # 🔥 FILTROS
            df = df[df["id"].apply(
                lambda movie_id: (
                    # ❗ SOLO aplicar inclusión si NO vino de actor
                    (actor_incluir_id in obtener_cast(movie_id) if (actor_incluir_id and not incluir_actor) else True)
                    and
                    (actor_excluir_id not in obtener_cast(movie_id) if actor_excluir_id else True)
                )
            )]

            print("Cantidad DESPUÉS de filtros:", len(df))

            if df.empty:
                print("😅 No encontré resultados con esos filtros")
            else:
                print("\n🎬 Te dejo algunas opciones que podrían gustarte:\n")

                # 🔥 MEZCLA REAL
                df = df.sample(frac=1).reset_index(drop=True)

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
        # CONTINUAR
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