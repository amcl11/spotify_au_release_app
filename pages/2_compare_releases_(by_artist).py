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
@st.cache_data
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
@st.cache_data
def fetch_data_for_selected_artist(artist_name):
    query = 'SELECT * FROM nmf_spotify_coverage WHERE "Artist" = %s'
    artist_data_df = pd.read_sql_query(query, engine, params=(artist_name,))
    return artist_data_df

st.subheader('If an artist has had multiple releases since 23rd February 2024, you can compare release coverage here.')
st.write('*This site only tracks releases that were added to NMF AU & NZ*')
st.write('--------------')
# Populate a selectbox with artist names
artists = fetch_artists_for_selectbox()


selected_artist = st.selectbox('Select an Artist to compare their tracks:', artists)

# Fetch and display data for the selected artist
if selected_artist:
    artist_data = fetch_data_for_selected_artist(selected_artist)

# Decide logic with 'artist_data' 
# Get the total followers for each title
total_followers_per_title = artist_data.groupby('Title')['Followers'].sum().reset_index()
    
# Sort the titles by total followers in descending order
sorted_titles = total_followers_per_title.sort_values(by='Followers', ascending=False)['Title']

titles_of_interest = artist_data['Title'].unique()
# Use this order for the x-axis order in the plot
artist_data_filtered = artist_data[artist_data['Title'].isin(titles_of_interest)]

# For viewing DF if needed
# st.dataframe(artist_data_filtered) 

total_playlist_adds = artist_data_filtered.groupby('Title')['Playlist'].nunique()

# Stacked bar chart for Reach comparision
fig = px.bar(artist_data_filtered, 
    x='Title', 
    y='Followers', 
    color='Playlist', 
    text='Playlist', 
    custom_data=['Position'],  # Include 'Position' in custom data for access in hovertemplate
    category_orders={'Title': sorted_titles.tolist()})
    
# Update the layout for a better visual representation
fig.update_layout(
    barmode='stack',
    title="Total Reach on Release (Fri-Wed)",
    xaxis_title="",
    yaxis_title="",
    legend_title="Playlists"
    )
    
# Customize hover data
# Customize hover data with 'Position' included
fig.update_traces(
    textposition='inside',
    hovertemplate="<b>Playlist:</b> %{text}<br>" + 
                  "<b>Playlist Reach:</b> %{y:,.0f}<br>" + 
                  "<b>Position:</b> %{customdata[0]}<extra></extra>"  # %{customdata[0]} accesses the first item in custom data
)

# Show the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)
st.write('*Hover over chart to check playlist position on release.*')
 