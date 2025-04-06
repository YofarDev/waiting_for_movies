# <<< START OF CORRECTED SCRIPT >>>
import requests
import os
import html # For escaping HTML characters
from datetime import datetime, date
import time # For potential delays if hitting rate limits
import webbrowser # <<< ADDED for opening file in browser


API_KEY = os.environ.get('TMDB_API_KEY')
if not API_KEY:
    print("Error: TMDb API key not found.")
    print("Please set the TMDB_API_KEY environment variable.")
    exit()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"
POSTER_SIZE = "w342"
DEFAULT_POSTER_FILENAME = "default_poster.png" # <<< ADDED constant for default poster
SEARCH_PERSON_ENDPOINT = f"{BASE_URL}/search/person"
PERSON_CREDITS_ENDPOINT = f"{BASE_URL}/person"
MOVIE_CREDITS_ENDPOINT = f"{BASE_URL}/movie" # Endpoint for movie details
OUTPUT_FILENAME = "directors_movies_current_detailed.html"
MAX_ACTORS_TO_SHOW = 5 # How many actors to list per movie


directors_list = [
    "Christopher Nolan",
    "Denis Villeneuve",
    "Greta Gerwig",
    "Quentin Tarantino",
    "Wes Anderson",
    "Jordan Peele",
    "Bong Joon-ho",
    # Add a director with upcoming/TBA movies for testing sorting
    # "James Cameron" # Example if needed
]


def get_director_id(name):
    # (Function remains the same as before)
    """Searches TMDb for a person and returns their ID."""
    params = {
        'api_key': API_KEY,
        'query': name,
        'language': 'en-US',
        'page': 1
    }
    try:
        response = requests.get(SEARCH_PERSON_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()

        if data['results']:
            directing_results = [p for p in data['results'] if p.get('known_for_department') == 'Directing']
            if directing_results:
                person = directing_results[0]
                print(f"Found ID {person['id']} for '{name}' (Best Match: {person['name']}, Dept: Directing)")
                return person['id']
            else:
                person = data['results'][0]
                print(f"Found ID {person['id']} for '{name}' (Best Match: {person['name']}, Dept: {person.get('known_for_department', 'N/A')}) - Using this ID.")
                return person['id']
        else:
            print(f"Could not find director ID for '{name}'")
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed for searching '{name}': {e}")
        return None
    except Exception as e:
        print(f"An error occurred while searching for '{name}': {e}")
        return None


def get_movie_cast(movie_id):
    """Fetches the cast for a specific movie ID."""
    if not movie_id:
        return []

    url = f"{MOVIE_CREDITS_ENDPOINT}/{movie_id}/credits"
    params = {'api_key': API_KEY, 'language': 'en-US'}
    cast_names = []

    # Optional: Add a small delay to avoid hitting rate limits too quickly
    # time.sleep(0.1) # Sleep for 100ms before each movie credit request

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'cast' in data:
            # Sort cast by 'order' (usually prominence) and take the top N
            sorted_cast = sorted(data['cast'], key=lambda x: x.get('order', 999))
            for actor in sorted_cast[:MAX_ACTORS_TO_SHOW]:
                cast_names.append(actor.get('name', 'Unknown Actor'))
        return cast_names

    except requests.exceptions.RequestException as e:
        print(f"  - WARN: API request failed for getting cast for movie ID {movie_id}: {e}")
        return [] # Return empty list on error
    except Exception as e:
        print(f"  - WARN: An error occurred while getting cast for movie ID {movie_id}: {e}")
        return []


def get_directed_movies(director_id):
    """
    Gets movie credits for a director, filters for current/upcoming/TBA,
    fetches cast for each, and sorts them (current year -> future -> TBA).
    """
    if not director_id:
        return []

    url = f"{PERSON_CREDITS_ENDPOINT}/{director_id}/movie_credits"
    params = {'api_key': API_KEY, 'language': 'en-US'}
    directed_movies = []
    current_year = datetime.now().year # <<< RESTORED current_year

    print(f"  Fetching movie credits for director ID {director_id}...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'crew' not in data:
            print(f"  Warning: No 'crew' data found for director ID {director_id}")
            return []

        crew_movies = [m for m in data.get('crew', []) if m.get('job') == 'Director']
        print(f"  Found {len(crew_movies)} raw directed movie entries. Filtering and fetching details...")

        movie_count = 0
        for movie in crew_movies:
            movie_count += 1
            print(f"   - Processing movie {movie_count}/{len(crew_movies)}: '{movie.get('title', 'N/A')}' (ID: {movie.get('id')})")
            release_date_str = movie.get('release_date')
            year = "N/A" # <<< Start with N/A as per original logic
            numeric_year = None # <<< RESTORED numeric_year
            release_date_obj = None # Store the date object for sorting

            if release_date_str:
                try:
                    # Use datetime.strptime for parsing, store date object
                    release_date_obj = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                    year = release_date_obj.year
                    numeric_year = year # <<< RESTORED numeric_year assignment
                except ValueError:
                    # Keep year as N/A if unparseable, but store date string if it exists
                    year = release_date_str if release_date_str else "N/A" # Keep original string if unparseable
                    if not release_date_str: # Explicitly handle empty string case
                        year = "N/A"


            # --- Filtering Logic (RESTORED from original script) ---
            keep_movie = False
            if numeric_year is not None:
                if numeric_year >= current_year:
                    keep_movie = True
            # Keep if year is specifically N/A or if release_date_str was non-empty but unparseable (often 'TBA' or similar)
            # <<< This logic handles the "unknown" case as requested >>>
            elif year == "N/A" or (release_date_str and not release_date_obj):
                 keep_movie = True
                 # Assign a marker for sorting if needed, though release_date_obj will be None
                 # Standardize non-dated entries to TBA for clarity in output/sorting value
                 year = "TBA"
            # --- End Filtering Logic ---

            if keep_movie: # <<< RESTORED conditional processing
                movie_id = movie.get('id')
                print(f"     Fetching cast for movie ID {movie_id}...")
                cast = get_movie_cast(movie_id) # Fetch cast

                poster_path = movie.get('poster_path')
                # <<< CHANGED: Use default filename if poster_path is missing >>>
                poster_url = f"{IMAGE_BASE_URL}{POSTER_SIZE}{poster_path}" if poster_path else DEFAULT_POSTER_FILENAME

                directed_movies.append({
                    'title': movie.get('title', 'N/A'),
                    'id': movie_id,
                    'overview': movie.get('overview', 'No synopsis available.'),
                    'release_date': release_date_str if release_date_str else "TBA",
                    'year': year, # Keep the determined year (int or "TBA")
                    'poster_url': poster_url, # <<< This will be full URL or default filename
                    'cast': cast, # Add the cast list
                    'sort_date': release_date_obj # Add the actual date object for sorting
                })
            else:
                 # <<< RESTORED skipping message >>>
                 print(f"     Skipping movie (Year: {year}, Filtered out).")


        print(f"  Sorting {len(directed_movies)} filtered movies...")
        # --- Sorting Logic (Applies to the FILTERED list) ---
        # Sort by date ascending: Current/Future dates sort chronologically.
        # TBA/N/A (where sort_date is None) come last.
        def sort_key(m):
            if m['sort_date'] is None:
                # Assign a date far in the future for TBA/None dates
                return date.max
            else:
                # Return the actual date for chronological sorting
                return m['sort_date']

        # Sort ascending (reverse=False). date.max ensures TBA/None are last.
        # <<< This correctly sorts current year -> future years -> TBA >>>
        directed_movies.sort(key=sort_key, reverse=False)

        return directed_movies

    except requests.exceptions.RequestException as e:
        print(f"API request failed for getting credits for ID {director_id}: {e}")
        return []
    except Exception as e:
        print(f"An error occurred while getting credits for ID {director_id}: {e}")
        return []


def generate_html(directors_data):
    """Generates the HTML content string with director and cast."""

    # --- CSS Styles ---
    # <<< CSS Remains unchanged from original >>>
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
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); /* Slightly wider cards */
        gap: 25px; /* Increased gap */
    }
    .movie-card {
        border: 1px solid #ddd; border-radius: 8px; padding: 15px;
        background-color: #fff; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        display: flex; flex-direction: column;
        overflow: hidden; transition: transform 0.2s ease-in-out;
    }
    .movie-card:hover { transform: scale(1.02); } /* Subtle hover */
    .movie-card img {
        max-width: 100%; height: auto; border-radius: 4px; margin-bottom: 10px;
        align-self: center; background-color: #eee; min-height: 200px; /* Taller min height */
        object-fit: cover; aspect-ratio: 2/3; /* Maintain poster aspect ratio */
        display: block; /* Ensure img is block for centering/margins */
        margin-left: auto; margin-right: auto; /* Center image */
        max-width: 200px; /* Limit image width within card */
    }
     /* Optional style for the default image placeholder */
     .movie-card img[src$="default_poster.png"] {
         /* Example: add a border or different background if the default is used */
         /* border: 1px dashed #ccc; */
         /* object-fit: contain; */
         background-color: #ddd; /* Lighter grey for placeholder */
     }
     /* This class was used before, kept for reference if needed but not actively used */
     .movie-card .no-poster {
        height: 300px; /* Match typical poster height */
        width: 200px; /* Match typical poster width */
        display: flex; align-items: center; justify-content: center;
        text-align: center; color: #888; font-size: 0.9em;
    }
    .movie-card h2 { /* Title */
        font-size: 1.25em; margin-top: 0; margin-bottom: 5px; color: #333;
        line-height: 1.2;
    }
    .movie-card .director { /* Director name */
        font-size: 0.9em; font-style: italic; color: #666;
        margin-bottom: 8px;
    }
    .movie-card .year { /* Year */
        font-weight: bold; color: #555; margin-bottom: 8px; font-size: 0.95em;
    }
    .movie-card .actors { /* Actors list */
        font-size: 0.85em; color: #777; margin-bottom: 10px;
        line-height: 1.3;
    }
    .movie-card .actors strong { color: #555; } /* Highlight "Starring" */
    .movie-card .synopsis { /* Synopsis */
        font-size: 0.9em; color: #444; flex-grow: 1;
        overflow-y: auto; max-height: 120px; /* Limit height */
        line-height: 1.4;
    }
    .hidden { display: none !important; }
    #no-movies-message {
        text-align: center; font-size: 1.1em; color: #888; margin-top: 30px;
        display: none; grid-column: 1 / -1;
    }
</style>
"""

    # --- JavaScript for Filtering (remains the same as original) ---
    script = """
<script>
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
        if (visibleCount === 0) {
            if (directorName === 'All') {
                msgElement.textContent = cards.length === 0 ? 'No current or upcoming movies were found for any director.' : 'No movies match the current filter (unexpected).';
            } else {
                msgElement.textContent = `No current or upcoming movies found for ${directorName}.`;
            }
            msgElement.style.display = 'block';
        } else {
            msgElement.style.display = 'none';
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
         const firstButton = document.querySelector('#filters button[onclick*="All"]');
         if (firstButton) firstButton.classList.add('active');

         const anyMovies = document.querySelector('.movie-card');
         if (!anyMovies) {
             const msgElement = document.getElementById('no-movies-message');
             msgElement.textContent = 'No current or upcoming movies were found for any of the specified directors.';
             msgElement.style.display = 'block';
         }
    });
</script>
"""

    # --- HTML Body ---
    # <<< H1 Title remains as original >>>
    body_content = "<h1>Current & Upcoming Movies by Director</h1>\n"

    # Filter Buttons
    body_content += '<div id="filters">\n'
    body_content += '    <button class="active" onclick="filterMovies(\'All\')">Show All</button>\n' # Start with All active
    directors_with_movies = []
    for director, movies in directors_data.items():
        # Check if the list exists and is not empty
        if movies: # Only add button if director has relevant movies
            safe_director_name = html.escape(director)
            body_content += f'    <button onclick="filterMovies(\'{safe_director_name}\')">{safe_director_name}</button>\n'
            directors_with_movies.append(director)
        # If director had no relevant movies, don't add a button
    body_content += '</div>\n'

    # Movie Cards Container
    body_content += '<div id="movie-container">\n'
    total_movies_found = 0

    # Iterate through directors *who have relevant movies*
    # The movies list is already filtered and sorted by get_directed_movies
    for director in directors_with_movies:
        movies = directors_data[director] # Get the pre-filtered, pre-sorted list
        safe_director_name = html.escape(director)
        for movie in movies:
            total_movies_found += 1

            # <<< CHANGED: Simplified poster HTML generation, always use img >>>
            poster_html = f'<img src="{html.escape(movie["poster_url"])}" alt="{html.escape(movie["title"])} Poster">'

            # Cast HTML (only if cast exists)
            cast_html = ""
            if movie['cast']:
                escaped_cast = [html.escape(actor) for actor in movie['cast']]
                cast_html = f'<p class="actors"><strong>Starring:</strong> {", ".join(escaped_cast)}</p>\n'

            body_content += f'  <div class="movie-card" data-director="{safe_director_name}">\n'
            body_content += f'    {poster_html}\n'
            body_content += f'    <h2>{html.escape(movie["title"])}</h2>\n'
            # Add Director Name
            body_content += f'    <p class="director">Directed by: {safe_director_name}</p>\n'
            # Year (Display 'TBA' if applicable)
            display_year = str(movie["year"]) # Ensure string for escaping
            body_content += f'    <p class="year">Year: {html.escape(display_year)}</p>\n'
            # Add Cast
            body_content += f'    {cast_html}'
            # Synopsis
            body_content += f'    <p class="synopsis">{html.escape(movie["overview"])}</p>\n'
            body_content += '  </div>\n'

    # Message placeholder
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


# <<< Print statement remains as original >>>
print("--- Fetching Current & Upcoming Movie Data (incl. Cast) for Directors ---")
print("--- NOTE: This may take longer due to fetching cast for each movie. ---")

all_movies_by_director = {}

start_time = time.time() # Start timer

for director_name in directors_list:
    print(f"\n----- Checking Director: {director_name} -----")
    director_id = get_director_id(director_name)
    if director_id:
        # get_directed_movies now filters, fetches cast, and sorts
        movies = get_directed_movies(director_id)
        all_movies_by_director[director_name] = movies
        # <<< Print statement reflects relevant movies found >>>
        print(f"----- Finished processing {director_name}. Found {len(movies)} relevant movies. -----")
    else:
        # Assign empty list if director ID not found
        all_movies_by_director[director_name] = []
        print(f"----- Could not retrieve data for {director_name}. -----")

end_time = time.time() # End timer
print(f"\n--- Data Fetching Complete (Took {end_time - start_time:.2f} seconds) ---")

print("\n--- Generating HTML Page ---")
html_content = generate_html(all_movies_by_director)

try:
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\nSuccessfully generated HTML file: {OUTPUT_FILENAME}")

    # <<< ADDED: Open file in browser >>>
    try:
        # Construct absolute file path URI
        file_path_abs = os.path.abspath(OUTPUT_FILENAME)
        # Ensure it's a file URI
        file_uri = f'file://{file_path_abs}'
        # On Windows, webbrowser might need the path without file:// prefix
        # but modern browsers usually handle file:// correctly. Let's stick to standard.
        if os.name == 'nt': # Optional: handle potential Windows quirk, but usually file:// works
             file_uri = f'file:///{file_path_abs.replace("\\", "/")}' # Use forward slashes

        webbrowser.open(file_uri)
        print(f"Attempting to open {OUTPUT_FILENAME} in the default browser...")
    except Exception as e:
        print(f"Could not automatically open the file in browser: {e}")
        print(f"Please open the file manually: {file_uri}")
    # <<< END of browser opening block >>>

except IOError as e:
    print(f"\nError writing HTML file: {e}")

print("\n--- Script Finished ---")

# <<< END OF CORRECTED SCRIPT >>>