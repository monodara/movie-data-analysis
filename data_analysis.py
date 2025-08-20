import pandas as pd
import logging
import matplotlib.pyplot as plt
from copy import deepcopy
from fpdf import FPDF

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_movie_data(input_file, output_file):
    """Process movie data and save to new CSV."""
    logging.info("Processing movie data...")
    movies = pd.read_csv(input_file)
    movies = movies[movies['status'] == "Released"]
    movies = movies[['original_title', 'release_date', 'genres', 'production_companies', 'production_countries', 'revenue','budget', 'runtime', 'vote_average']]
    movies = movies.dropna()
    movies['profit'] = movies['revenue'] - movies['budget']
    movies['release_date'] = pd.to_datetime(movies['release_date'])
    movies['release_year'] = movies['release_date'].dt.year
    movies = movies.drop(columns='release_date')
    movies.to_csv(output_file, index=False)
    logging.info(f"Processed data saved to {output_file}.")

def analyze_movie_data(input_file):
    """Perform extended analysis on processed movie data and generate PDF report."""
    logging.info(f"Analyzing data from {input_file}...")
    df = pd.read_csv(input_file)
    df['total_numbers'] = 1
    movies_each_year = df.groupby('release_year').agg(total_numbers_a_year=('total_numbers','sum'),
                       year_revenue=('revenue', 'sum'),
                       year_budget =('budget', 'sum'),
                       year_profit =('profit', 'sum'))

    # Chart 1: Movies released per year
    plt.figure(figsize=(22,7))
    plt.bar(movies_each_year.index, movies_each_year['total_numbers_a_year'], color="purple")
    plt.ylabel("numbers", fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.title("Movies released every year")
    plt.savefig("movies_per_year.png")

    # Chart 2: Capital of Movies
    plt.figure(figsize=(22,7))
    plt.plot(movies_each_year.index, movies_each_year['year_budget'], color="coral", linewidth=3)
    plt.plot(movies_each_year.index, movies_each_year['year_revenue'], color="green", linewidth=3)
    plt.plot(movies_each_year.index, movies_each_year['year_profit'], color="blue", linewidth=3)
    plt.grid(axis="y")
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Capital ($)', fontsize=14)
    plt.legend(["budget","revenue","profit"], fontsize=13)
    plt.yticks(fontsize=14)
    plt.title("Capital of Movies")
    plt.savefig("capital_of_movies.png")

    # Chart 3: Genre distribution pie chart
    all_genres = set()
    for item in df['genres']:
        genres = eval(item)
        for g in genres:
            all_genres.add(g['name'])
    all_genres = list(all_genres)
    genre_df = deepcopy(df)
    for genre in all_genres:
        genre_df[genre] = genre_df['genres'].str.contains(genre).apply(lambda x: 1 if x else 0)
    genre_sum = genre_df[all_genres].sum()
    plt.figure(figsize=(16, 8))
    plt.pie(genre_sum, labels=genre_sum.index, autopct="%1.2f%%")
    plt.title("Proportion of movie genres")
    plt.savefig("genre_pie_chart.png")

    # Chart 4: Runtime vs Vote
    plt.figure(figsize=(22,10))
    plt.scatter(df['runtime'], df['vote_average'])
    plt.xlabel("runtime")
    plt.ylabel("average vote")
    plt.title("Relationship between runtime & vote")
    plt.grid(True)
    plt.savefig("runtime_vs_vote.png")

    # Chart 5: Revenue vs Vote
    plt.figure(figsize=(22,10))
    plt.scatter(df['revenue'], df['vote_average'])
    plt.xlabel("revenue")
    plt.ylabel("average vote")
    plt.title("Relationship between revenue & vote")
    plt.grid(True)
    plt.savefig("revenue_vs_vote.png")

    # Chart 6: Production countries pie chart
    all_countries = set()
    for item in df['production_countries']:
        countries = eval(item)
        for c in countries:
            all_countries.add(c['name'])
    all_countries = list(all_countries)
    country_df = deepcopy(df)
    for country in all_countries:
        country_df[country] = country_df['production_countries'].str.contains(country).apply(lambda x: 1 if x else 0)
    country_sum = country_df[all_countries].sum().sort_values(ascending=False)
    top_countries = country_sum[country_sum > 10]
    others = country_sum[country_sum <= 10].sum()
    pie_data = top_countries.copy()
    pie_data['Others'] = others
    plt.figure(figsize=(16, 8))
    plt.pie(pie_data, labels=pie_data.index, autopct="%1.2f%%")
    plt.title("Proportion of production countries")
    plt.savefig("country_pie_chart.png")

    # Generate PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Movie Data Analysis Report", ln=True, align='C')
    pdf.ln(10)
    charts = [
        ("Movies Released Per Year", "movies_per_year.png"),
        ("Capital of Movies", "capital_of_movies.png"),
        ("Proportion of Movie Genres", "genre_pie_chart.png"),
        ("Runtime vs Vote", "runtime_vs_vote.png"),
        ("Revenue vs Vote", "revenue_vs_vote.png"),
        ("Production Countries", "country_pie_chart.png")
    ]
    for title, img in charts:
        pdf.add_page()
        pdf.cell(200, 10, txt=title, ln=True)
        pdf.image(img, x=10, y=30, w=180)
    pdf.output("movie_analysis_report.pdf")
    logging.info("PDF report generated: movie_analysis_report.pdf")