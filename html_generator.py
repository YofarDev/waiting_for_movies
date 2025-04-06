# html_generator.py
import html
from datetime import date

# Import configuration needed for HTML generation
from config import DEFAULT_POSTER_FILENAME

def generate_html(directors_data):
    """
    Generates the HTML content string. Movies are sorted globally by year
    for the initial view, but retain director info for filtering.
    """

    styles = """
<style>
    body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; }
    h1 { text-align: center; color: #333; }
    #filters { margin-bottom: 20px; text-align: center; }
    #filters button {
        padding: 10px 15px; margin: 5px; cursor: pointer;
        border: 1px solid #ccc; background-color: #eee; border-radius: 4px;
    }
    #filters button.active {
        background-color: #007bff; color: white; border-color: #0056b3;
    }
    #movie-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 25px;
    }
    .movie-card {
        border: 1px solid #ddd; border-radius: 8px; padding: 15px;
        background-color: #fff; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        display: flex; flex-direction: column;
        overflow: hidden; transition: transform 0.2s ease-in-out;
    }
    .movie-card:hover { transform: scale(1.02); }
    .movie-card img {
        max-width: 100%; height: auto; border-radius: 4px; margin-bottom: 10px;
        align-self: center; background-color: #eee; min-height: 200px;
        object-fit: cover; aspect-ratio: 2/3;
        display: block; margin-left: auto; margin-right: auto;
        max-width: 200px;
    }
    .movie-card img[src$="default_poster.png"] { background-color: #ddd; }
    .movie-card h2 { font-size: 1.25em; margin: 0 0 5px 0; color: #333; line-height: 1.2; }
    .movie-card .director { font-size: 0.9em; font-style: italic; color: #666; margin-bottom: 8px; }
    .movie-card .year { font-weight: bold; color: #555; margin-bottom: 8px; font-size: 0.95em; }
    .movie-card .actors { font-size: 0.85em; color: #777; margin-bottom: 10px; line-height: 1.3; }
    .movie-card .actors strong { color: #555; }
    .movie-card .synopsis { font-size: 0.9em; color: #444; flex-grow: 1; overflow-y: auto; max-height: 120px; line-height: 1.4; }
    .hidden { display: none !important; }
    #no-movies-message { text-align: center; font-size: 1.1em; color: #888; margin-top: 30px; display: none; grid-column: 1 / -1; }
</style>
"""

    script = """
<script>
    // JavaScript for filtering remains the same
    function filterMovies(directorName) {
        const cards = document.querySelectorAll('.movie-card');
        const buttons = document.querySelectorAll('#filters button');
        const noMoviesMsg = document.getElementById('no-movies-message');
        let visibleCount = 0;

        buttons.forEach(button => {
            button.classList.toggle('active', button.textContent === directorName || (directorName === 'All' && button.textContent === 'Show All'));
        });

        cards.forEach(card => {
            const cardDirector = card.getAttribute('data-director');
            const isVisible = directorName === 'All' || cardDirector === directorName;
            card.classList.toggle('hidden', !isVisible);
            if (isVisible) visibleCount++;
        });

        const msgElement = document.getElementById('no-movies-message');
        msgElement.style.display = visibleCount === 0 ? 'block' : 'none';
        if (visibleCount === 0) {
            if (directorName === 'All') {
                 msgElement.textContent = 'No current or upcoming movies were found for any director.';
            } else {
                 msgElement.textContent = `No current or upcoming movies found for ${directorName}.`;
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
         const firstButton = document.querySelector('#filters button[onclick*="All"]');
         if (firstButton) firstButton.classList.add('active');
         if (!document.querySelector('.movie-card')) {
             const msgElement = document.getElementById('no-movies-message');
             msgElement.textContent = 'No current or upcoming movies were found for any specified directors.';
             msgElement.style.display = 'block';
         }
    });
</script>
"""

    body_content = "<h1>Current & Upcoming Movies by Director</h1>\n"

    # --- Aggregate movies and sort globally by year ---
    all_movies_flat = []
    directors_with_movies_for_buttons = set()

    for director, movies in directors_data.items():
        if movies:
            directors_with_movies_for_buttons.add(director)
            for movie in movies:
                movie_copy = movie.copy()
                movie_copy['director_name'] = director
                all_movies_flat.append(movie_copy)

    # Use the same sort key logic as in tmdb_api.py for consistency
    def sort_key(m):
        return m.get('sort_date') if m.get('sort_date') is not None else date.max
    all_movies_flat.sort(key=sort_key, reverse=False)
    # --- End aggregation and sorting ---

    # Filter Buttons
    body_content += '<div id="filters">\n'
    body_content += '    <button class="active" onclick="filterMovies(\'All\')">Show All</button>\n'
    for director in sorted(list(directors_with_movies_for_buttons)):
         safe_director_name = html.escape(director)
         body_content += f'    <button onclick="filterMovies(\'{safe_director_name}\')">{safe_director_name}</button>\n'
    body_content += '</div>\n'

    # Movie Cards Container
    body_content += '<div id="movie-container">\n'

    # Generate cards from the globally sorted list
    for movie in all_movies_flat:
        director_name = movie['director_name']
        safe_director_name = html.escape(director_name)

        poster_html = f'<img src="{html.escape(movie["poster_url"])}" alt="{html.escape(movie["title"])} Poster">'

        cast_html = ""
        if movie.get('cast'):
            escaped_cast = [html.escape(actor) for actor in movie['cast']]
            cast_html = f'<p class="actors"><strong>Starring:</strong> {", ".join(escaped_cast)}</p>\n'

        body_content += f'  <div class="movie-card" data-director="{safe_director_name}">\n'
        body_content += f'    {poster_html}\n'
        body_content += f'    <h2>{html.escape(movie["title"])}</h2>\n'
        body_content += f'    <p class="director">Directed by: {safe_director_name}</p>\n'
        body_content += f'    <p class="year">Year: {html.escape(str(movie["year"]))}</p>\n'
        body_content += f'    {cast_html}'
        body_content += f'    <p class="synopsis">{html.escape(movie["overview"])}</p>\n'
        body_content += '  </div>\n'

    body_content += '<p id="no-movies-message" style="display: none;"></p>\n'
    body_content += '</div>\n' # Close movie-container

    # Combine all parts
    html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Current & Upcoming Movies by Director</title>
    {styles}
</head>
<body>
    {body_content}
    {script}
</body>
</html>
"""
    return html_output