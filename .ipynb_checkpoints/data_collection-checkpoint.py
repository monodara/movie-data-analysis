import json
import requests
import csv
import logging
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Key
load_dotenv()
api_key_TMDB = os.getenv("TMDB_API_KEY")
if not api_key_TMDB:
    raise ValueError("TMDB_API_KEY environment variable not set.")
# API URL Prefixes
TMDB_url = "https://api.themoviedb.org/3/movie/"
api_prefix_TMDB = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key_TMDB}&page="

def fetch_movie_details(movie_id):
    """Fetch detailed movie data by ID."""
    try:
        url = f"{TMDB_url}{movie_id}?api_key={api_key_TMDB}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch movie ID {movie_id}: {e}")
        return None

def collect_movie_data(output_file, max_pages=500):
    """Collect movie data from TMDB and save to CSV."""
    logging.info(f"Starting data collection for {max_pages} pages...")
    flag = True
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for pageNo in tqdm(range(1, max_pages + 1), desc="Collecting pages"):
            url = f"{api_prefix_TMDB}{pageNo}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                page_result = response.json().get('results', [])
                for result in page_result:
                    movie_id = result.get('id')
                    movie_data = fetch_movie_details(movie_id)
                    if movie_data:
                        if flag:
                            keys = list(movie_data.keys())
                            writer.writerow(keys)
                            flag = False
                        writer.writerow([movie_data.get(k, '') for k in keys])
            except requests.RequestException as e:
                logging.error(f"Failed to fetch page {pageNo}: {e}")

    logging.info("Data collection completed.")