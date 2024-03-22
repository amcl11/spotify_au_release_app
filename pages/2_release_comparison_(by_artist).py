import streamlit as st
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

# Function to fetch all data for artists with more than one unique title
@st.cache_data(show_spinner="Fetching artists...")
def fetch_artists_for_selectbox():
    query = """
    SELECT "Artist"
    FROM nmf_spotify_coverage 
    GROUP BY "Artist" 
    HAVING COUNT(DISTINCT "Title") > 1
    """
    artists_df = pd.read_sql_query(query, engine)
    return artists_df['Artist'].tolist()

# Function to fetch all available data for a selected artist
@st.cache_data(show_spinner="Loading data...")
def fetch_data_for_selected_artist(artist_name):
    query = 'SELECT * FROM nmf_spotify_coverage WHERE "Artist" = %s'
    artist_data_df = pd.read_sql_query(query, engine, params=(artist_name,))
    return artist_data_df

st.subheader('Release Comparison (By Artist):')
st.write('Data available from 23rd Feb 2024 onwards')
st.markdown(
    '<p style="font-size: 14px;">This site only tracks releases that were added to NMF AU & NZ</p>', 
    unsafe_allow_html=True
)
st.write('--------------')

# Populate a selectbox with artist names
artists = fetch_artists_for_selectbox()

selected_artist = st.selectbox('Select Artist:', artists)

# Fetch and display data for the selected artist
if selected_artist:
    artist_data = fetch_data_for_selected_artist(selected_artist)

# Convert 'Date' from string to datetime format
artist_data['Date'] = pd.to_datetime(artist_data['Date'])

# Use the existing 'add_ordinal' function to format the date
def add_ordinal(day):
    return str(day) + ("th" if 4 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th"))

# Format 'Date' as "22nd March, 2024"
artist_data['Formatted_Date'] = artist_data['Date'].dt.day.apply(add_ordinal) + " " + artist_data['Date'].dt.strftime('%B, %Y')

# Get the total followers for each title
total_followers_per_title = artist_data.groupby('Title')['Followers'].sum().reset_index()
    
# Sort the titles by total followers in descending order
sorted_titles = total_followers_per_title.sort_values(by='Followers', ascending=False)['Title']

titles_of_interest = artist_data['Title'].unique()

# Use this order for the x-axis order in the plot
artist_data_filtered = artist_data[artist_data['Title'].isin(titles_of_interest)]

# Stacked bar chart for Reach comparision
fig = px.bar(artist_data_filtered, 
    x='Title', 
    y='Followers', 
    color='Playlist', 
    text='Playlist', 
    custom_data=['Position', 'Formatted_Date'],  # Add 'Formatted_Date' to custom data
    category_orders={'Title': sorted_titles.tolist()})

# Update the layout for a better visual representation
fig.update_layout(
    barmode='stack',
    title={
        'text': "Total Reach on Release (Fri-Wed)",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title="",
    yaxis_title="",
    legend_title="Playlists",
    height=400,
    yaxis=dict(
        tick0=0,
        dtick=500000
    )
)

# Customize hover data
fig.update_traces(
    textposition='inside',
    hovertemplate="<b>Release Date:</b> %{customdata[1]}<br>" +  # Access 'Formatted_Date' from custom data
                  "<b>Playlist:</b> %{text}<br>" +
                  "<b>Playlist Reach:</b> %{y:,.0f}<br>" +
                  "<b>Position:</b> %{customdata[0]}<extra></extra>"
)

st.write(
        """
        <style>
            .my-text {
                font-size: 11px;
                font-family: monospace;
            }
        </style>
        <p class="my-text">Hover over chart for additional info:</p>
        """,
        unsafe_allow_html=True,
    )
# Show the figure in Streamlit
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})