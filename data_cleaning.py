import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_movie_data(input_file, output_file):
    """Clean raw movie data and save to new CSV."""
    logging.info(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)

    # Drop columns with too many missing values
    df = df.dropna(axis=1, thresh=len(df) * 0.5)

    # Drop rows with missing critical fields
    df = df.dropna(subset=['title', 'release_date', 'revenue', 'runtime'])

    # Convert release_date to datetime
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Remove rows with invalid dates
    df = df.dropna(subset=['release_date'])

    # Save cleaned data
    df.to_csv(output_file, index=False)
    logging.info(f"Cleaned data saved to {output_file}.")