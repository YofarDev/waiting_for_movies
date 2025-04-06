# main.py
import os
import time
import webbrowser

# Import necessary components from other modules
from config import directors_list, OUTPUT_FILENAME
from tmdb_api import get_director_id, get_directed_movies
from html_generator import generate_html

def run():
    """Main function to orchestrate fetching data and generating HTML."""
    print("--- Fetching Current & Upcoming Movie Data ---")

    all_movies_by_director = {}
    start_time = time.time()

    for director_name in directors_list:
        print(f"\n----- Processing Director: {director_name} -----")
        director_id = get_director_id(director_name)
        if director_id:
            movies = get_directed_movies(director_id)
            all_movies_by_director[director_name] = movies
            print(f"----- Found {len(movies)} relevant movies for {director_name}. -----")
        else:
            all_movies_by_director[director_name] = [] # Assign empty list if failed
            print(f"----- Could not retrieve data for {director_name}. -----")

    end_time = time.time()
    print(f"\n--- Data Fetching Complete (Took {end_time - start_time:.2f} seconds) ---")

    print("\n--- Generating HTML Page ---")
    html_content = generate_html(all_movies_by_director)

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nSuccessfully generated HTML file: {OUTPUT_FILENAME}")

        # Attempt to open the generated file in the default browser
        try:
            file_path_abs = os.path.abspath(OUTPUT_FILENAME)
            file_uri = f'file:///{file_path_abs.replace("\\", "/")}' # Create file URI
            webbrowser.open(file_uri)
            print(f"Attempting to open {OUTPUT_FILENAME} in browser...")
        except Exception as e:
            print(f"Could not automatically open file in browser: {e}")
            print(f"Please open the file manually: {file_uri}")

    except IOError as e:
        print(f"\nError writing HTML file: {e}")

    print("\n--- Script Finished ---")

if __name__ == "__main__":
    # Ensure the script runs only when executed directly
    run()