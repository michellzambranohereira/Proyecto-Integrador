# Proyecto-Integrador

Proyecto: Recomendador de Películas con Chatbot

Descripción: Repositorio correspondiente al Proyecto Final Integrador de la Tecnicatura en Ciencia de Datos e Inteligencia Artificial, desarrollado por Michell Andreina Zambrano Hereira.

El proyecto consiste en un sistema recomendador de películas basado en un chatbot capaz de interpretar consultas en lenguaje natural y generar recomendaciones personalizadas utilizando información obtenida desde la API de TMDB.


Objetivo: Ayudar a los usuarios a decidir qué película ver mediante consultas en lenguaje natural, permitiendo obtener recomendaciones rápidas e interactivas.

Funcionalidades:

- Recomendación de películas por género.
- Recomendación por actor.
- Inclusión y exclusión de actores.
- Interpretación básica de lenguaje natural.
- Integración con API de TMDB.
- Interfaz gráfica desarrollada en Streamlit.
- Visualización de título, puntuación y sinopsis.

Tecnologías:

- Python
- Streamlit
- Pandas
- spaCy
- Requests
- API TMDB

Cómo usar:

1. Clonar el repositorio

git clone URL_DEL_REPOSITORIO

2. Instalar dependencias:

pip install -r requirements.txt

- En caso de que spaCy no instale automáticamente el modelo en español python -m spacy download es_core_news_sm

3. Ejecutar:

streamlit run app.py o streamlit run source/app.py

Estado del proyecto:

Proyecto desarrollado como MVP (Producto Mínimo Viable), con posibilidad de incorporar mejoras futuras relacionadas con modelos de lenguaje más avanzados y sistemas de recomendación más complejos.