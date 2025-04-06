# tmdb_api.py
from datetime import date, datetime

import requests

# Import configuration from config.py
from config import (
    API_KEY,
    DEFAULT_POSTER_FILENAME,
    IMAGE_BASE_URL,
    MAX_ACTORS_TO_SHOW,
    MOVIE_CREDITS_ENDPOINT,
    PERSON_CREDITS_ENDPOINT,
    POSTER_SIZE,
    SEARCH_PERSON_ENDPOINT,
)


def get_director_id(name):
    """Searches TMDb for a person by name and returns their ID."""
    params = {"api_key": API_KEY, "query": name, "language": "en-US", "page": 1}
    try:
        response = requests.get(SEARCH_PERSON_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()

        if data["results"]:
            # Prioritize results where known_for_department is Directing
            directing_results = [
                p
                for p in data["results"]
                if p.get("known_for_department") == "Directing"
            ]
            if directing_results:
                person = directing_results[0]
                print(
                    f"Found ID {person['id']} for '{name}' (Best Match: {person['name']}, Dept: Directing)"
                )
                return person["id"]
            else:
                # Fallback to the first result if no specific director match
                person = data["results"][0]
                print(
                    f"Found ID {person['id']} for '{name}' (Best Match: {person['name']}, Dept: {person.get('known_for_department', 'N/A')}) - Using this ID."
                )
                return person["id"]
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
    """Fetches the top N cast members for a specific movie ID."""
    if not movie_id:
        return []

    url = f"{MOVIE_CREDITS_ENDPOINT}/{movie_id}/credits"
    params = {"api_key": API_KEY, "language": "en-US"}
    cast_names = []

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "cast" in data:
            # Sort cast by 'order' (prominence) and take the top N
            sorted_cast = sorted(data["cast"], key=lambda x: x.get("order", 999))
            for actor in sorted_cast[:MAX_ACTORS_TO_SHOW]:
                cast_names.append(actor.get("name", "Unknown Actor"))
        return cast_names

    except requests.exceptions.RequestException as e:
        print(f"  - WARN: API request failed getting cast for movie ID {movie_id}: {e}")
        return []
    except Exception as e:
        print(f"  - WARN: An error occurred getting cast for movie ID {movie_id}: {e}")
        return []


def get_directed_movies(director_id):
    """
    Gets movie credits for a director, filters for current/upcoming/TBA,
    fetches cast, and sorts them (current year -> future -> TBA).
    """
    if not director_id:
        return []

    url = f"{PERSON_CREDITS_ENDPOINT}/{director_id}/movie_credits"
    params = {"api_key": API_KEY, "language": "en-US"}
    directed_movies = []
    current_year = datetime.now().year

    print(f"  Fetching movie credits for director ID {director_id}...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "crew" not in data:
            print(f"  Warning: No 'crew' data found for director ID {director_id}")
            return []

        crew_movies = [m for m in data.get("crew", []) if m.get("job") == "Director"]
        print(
            f"  Found {len(crew_movies)} raw directed entries. Filtering/fetching details..."
        )

        for movie in crew_movies:
            release_date_str = movie.get("release_date")
            year = "N/A"
            numeric_year = None
            release_date_obj = None  # For precise date sorting

            if release_date_str:
                try:
                    release_date_obj = datetime.strptime(
                        release_date_str, "%Y-%m-%d"
                    ).date()
                    year = release_date_obj.year
                    numeric_year = year
                except ValueError:
                    year = release_date_str  # Keep original string if unparseable (like 'TBA')
            else:  # Handle null/empty release date
                year = "TBA"  # Explicitly mark as TBA

            # --- Filter: Keep movies >= current year OR marked as TBA/unparseable ---
            keep_movie = False
            if numeric_year is not None:
                if numeric_year >= current_year:
                    keep_movie = True
            elif year == "TBA" or (
                release_date_str and not release_date_obj
            ):  # Includes unparseable & explicitly set TBA
                keep_movie = True
                year = "TBA"  # Standardize display value

            if keep_movie:
                movie_id = movie.get("id")
                # print(f"     Fetching cast for movie ID {movie_id}...") # Less verbose logging
                cast = get_movie_cast(movie_id)

                poster_path = movie.get("poster_path")
                poster_url = (
                    f"{IMAGE_BASE_URL}{POSTER_SIZE}{poster_path}"
                    if poster_path
                    else DEFAULT_POSTER_FILENAME
                )

                directed_movies.append(
                    {
                        "title": movie.get("title", "N/A"),
                        "id": movie_id,
                        "overview": movie.get("overview", "No synopsis available."),
                        "release_date": release_date_str if release_date_str else "TBA",
                        "year": year,
                        "poster_url": poster_url,
                        "cast": cast,
                        "sort_date": release_date_obj,  # Use actual date obj for sorting
                    }
                )
            # else:
            # print(f"     Skipping movie '{movie.get('title', 'N/A')}' (Year: {year}, Filtered out).") # Less verbose

        # Sort the filtered list: valid dates ascending, None/'TBA' dates last
        def sort_key(m):
            # Place items with no valid sort_date (None) last by returning a max date value
            return m["sort_date"] if m["sort_date"] is not None else date.max

        directed_movies.sort(key=sort_key, reverse=False)
        print(f"  Sorted {len(directed_movies)} relevant movies.")
        return directed_movies

    except requests.exceptions.RequestException as e:
        print(f"API request failed getting credits for ID {director_id}: {e}")
        return []
    except Exception as e:
        print(f"An error occurred getting credits for ID {director_id}: {e}")
        return []
