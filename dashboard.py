import pandas as pd
import dash
from dash import dcc, html
from dash import Input, Output
import plotly.express as px
import logging
import ast

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the processed movie data
try:
    df = pd.read_csv('processed_movies.csv')
except FileNotFoundError:
    logging.error("processed_movies.csv not found. Please run the pipeline first.")
    exit()

# --- Feature Engineering for Dashboard ---
# Calculate Profitability Ratio (ROI)
# To avoid division by zero or infinity, replace 0 budget with a small number (e.g., 1)
df['profitability_ratio'] = df['profit'] / df['budget'].replace(0, 1)

# Classify movies as "Hit" or "Flop"
df['verdict'] = df.apply(lambda row: 'Hit' if row['revenue'] > 2 * row['budget'] else 'Flop', axis=1)

# Extract genres and countries for filtering
def get_list_from_str(s):
    try:
        return [item['name'] for item in ast.literal_eval(s)]
    except (SyntaxError, TypeError, NameError):
        return []

df['genre_list'] = df['genres'].apply(get_list_from_str)
df['country_list'] = df['production_countries'].apply(get_list_from_str)

# Create a long-format DataFrame for genres and countries for easier filtering
df_genres = df.explode('genre_list')
df_countries = df.explode('country_list')

# Get unique lists for dropdowns
all_genres = sorted(df_genres['genre_list'].dropna().unique())
all_countries = sorted(df_countries['country_list'].dropna().unique())

# --- Initialize the Dash App ---
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Movie Data Analysis Dashboard"

# --- Dashboard Layout ---
app.layout = html.Div([
    html.H1("Interactive Movie Data Analysis", style={'textAlign': 'center'}),

    # -- Filters --
    html.Div([
        html.Div([
            html.Label("Select Release Year Range:"),
            dcc.RangeSlider(
                id='year-slider',
                min=df['release_year'].min(),
                max=df['release_year'].max(),
                value=[df['release_year'].min(), df['release_year'].max()],
                marks={str(year): str(year) for year in range(df['release_year'].min(), df['release_year'].max() + 1, 5)},
                step=1
            ),
        ], className="six columns"),

        html.Div([
            html.Label("Select Genre:"),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': 'All Genres', 'value': 'all'}] + [{'label': genre, 'value': genre} for genre in all_genres],
                value='all'
            ),
        ], className="three columns"),

        html.Div([
            html.Label("Select Production Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': 'All Countries', 'value': 'all'}] + [{'label': country, 'value': country} for country in all_countries],
                value='all'
            ),
        ], className="three columns"),
    ], className="row", style={'marginBottom': '20px'}),

    # -- Charts --
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-vote-scatter')
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='profit-bar-chart')
        ], className="six columns"),
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Graph(id='genre-sunburst')
        ], className="six columns"),
        html.Div([
            dcc.Graph(id='country-choropleth')
        ], className="six columns"),
    ], className="row"),
])

# --- Callback Functions for Interactivity ---
@app.callback(
    [Output('revenue-vote-scatter', 'figure'),
     Output('profit-bar-chart', 'figure'),
     Output('genre-sunburst', 'figure'),
     Output('country-choropleth', 'figure')],
    [Input('year-slider', 'value'),
     Input('genre-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_charts(year_range, selected_genre, selected_country):
    # Filter data based on user input
    filtered_df = df[
        (df['release_year'] >= year_range[0]) &
        (df['release_year'] <= year_range[1])
    ]

    if selected_genre != 'all':
        filtered_df = filtered_df[filtered_df['genre_list'].apply(lambda x: selected_genre in x)]

    if selected_country != 'all':
        filtered_df = filtered_df[filtered_df['country_list'].apply(lambda x: selected_country in x)]

    # Chart 1: Revenue vs. Vote Average Scatter Plot
    scatter_fig = px.scatter(
        filtered_df,
        x='revenue',
        y='vote_average',
        hover_name='original_title',
        color='verdict',
        color_discrete_map={'Hit': 'green', 'Flop': 'red'},
        title='Revenue vs. Vote Average'
    )
    scatter_fig.update_layout(transition_duration=500)

    # Chart 2: Top 10 Most Profitable Movies Bar Chart
    top_10_profitable = filtered_df.nlargest(10, 'profit')
    bar_fig = px.bar(
        top_10_profitable,
        x='profit',
        y='original_title',
        orientation='h',
        title='Top 10 Most Profitable Movies'
    )
    bar_fig.update_layout(yaxis={'categoryorder':'total ascending'}, transition_duration=500)


    # Chart 3: Genre Profitability Sunburst Chart
    genre_profit_df = filtered_df.explode('genre_list').groupby('genre_list').agg({'profit': 'sum'}).reset_index()
    sunburst_fig = px.sunburst(
        genre_profit_df,
        path=['genre_list'],
        values='profit',
        title='Profitability by Genre'
    )
    sunburst_fig.update_layout(transition_duration=500)

    # Chart 4: Movie Production by Country Choropleth Map
    country_count_df = filtered_df.explode('country_list').groupby('country_list').size().reset_index(name='movie_count')
    choropleth_fig = px.choropleth(
        country_count_df,
        locations='country_list',
        locationmode='country names',
        color='movie_count',
        hover_name='country_list',
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Number of Movies Produced by Country'
    )
    choropleth_fig.update_layout(transition_duration=500)


    return scatter_fig, bar_fig, sunburst_fig, choropleth_fig

# --- Run the App ---
if __name__ == '__main__':
    # Before running, make sure you have a `processed_movies.csv` file.
    # You can generate it by running the main pipeline: `python pipeline.py`
    # Note: You will need a TMDB API key for the pipeline to work.
    logging.info("Starting the interactive dashboard...")
    logging.info("Go to http://127.0.0.1:8050/ in your web browser.")
    app.run(debug=True)
