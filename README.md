# Waiting For Movies

A Python script that tracks current and upcoming movies from your favorite directors.

## Features
- Fetches movie data from The Movie Database (TMDB) API
- Generates a clean HTML page with all movies
- Automatically opens the results in your browser

## Requirements
- Python 3.x
- TMDB API key (set in config.py)

## Usage
1. Edit `config.py` to add your directors and API key
2. Run the script:
```bash
python main.py
```
3. View the generated HTML file in your browser

## Output
The script creates `directors_movies_current_detailed.html` with all the movies.
