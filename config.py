# config.py
import os

# --- TMDb API Configuration ---
API_KEY = os.environ.get('TMDB_API_KEY')
if not API_KEY:
    print("Error: TMDb API key not found.")
    print("Please set the TMDB_API_KEY environment variable.")
    exit()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"
POSTER_SIZE = "w342"
DEFAULT_POSTER_FILENAME = "default_poster.png"

SEARCH_PERSON_ENDPOINT = f"{BASE_URL}/search/person"
PERSON_CREDITS_ENDPOINT = f"{BASE_URL}/person"
MOVIE_CREDITS_ENDPOINT = f"{BASE_URL}/movie"

# --- Script Configuration ---
OUTPUT_FILENAME = "directors_movies_current_detailed.html"
MAX_ACTORS_TO_SHOW = 5

# --- Data ---
directors_list = [
    "Christopher Nolan",
    "Denis Villeneuve",
    "Greta Gerwig",
    "Quentin Tarantino",
    "Wes Anderson",
    "Jordan Peele",
    "Bong Joon-ho",
    "Hirokazu Kore-eda",
    "Céline Sciamma",
    "Nathan Ambrosioni",
    "Julia Ducournau",
    "Martin Scorsese",
    "Damien Chazelle",
    "George Miller ",
    "Yorgos Lanthimos",
    "Ari Aster",
    "Mike Cheslik",
    "Park Chan-wook",
    "Thomas Vinterberg",
    "Martin McDonagh",
    "Joel Coen",
    "M. Night Shyamalan",
]