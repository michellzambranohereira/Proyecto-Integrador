import requests

API_KEY = "903d94755233e0bd7a4a04e0de529bab"

url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=es-ES"

response = requests.get(url)
data = response.json()

for movie in data["results"][:5]:
    print(movie["title"], "-", movie["vote_average"])
