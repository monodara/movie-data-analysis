import argparse
from data_collection import collect_movie_data
from data_cleaning import clean_movie_data
from data_analysis import process_movie_data, analyze_movie_data

def main():
    parser = argparse.ArgumentParser(description="Run movie data pipeline")
    parser.add_argument('--pages', type=int, default=500, help='Number of pages to collect from TMDB')
    args = parser.parse_args()

    raw_file = 'movie_dataset_raw.csv'
    cleaned_file = 'movie_dataset_cleaned.csv'
    processed_file = 'processed_movies.csv'

    # Step 1: Collect raw data
    collect_movie_data(raw_file, max_pages=args.pages)

    # Step 2: Clean the data
    clean_movie_data(raw_file, cleaned_file)

    # Step 3: Process the data
    process_movie_data(cleaned_file, processed_file)

    # Step 4: Analyze the data and generate report
    analyze_movie_data(processed_file)

if __name__ == '__main__':
    main()