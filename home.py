import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import plotly.express as px
from theme import set_theme
from sqlalchemy import create_engine, text
import os

set_theme()

# Setup DATABASE_URL and engine
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

# Load cover images and cover artist data from saved dictionaries as JSON
with open('cover_art_data.json') as f:
    data = json.load(f)

cover_art_dict = data['filtered_cover_art_dict']
cover_artist_dict = data['cover_artist_dict']

def get_most_added_artist(engine):
    query = """
    SELECT "Artist", COUNT(*) AS count
    FROM nmf_spotify_coverage
    WHERE "Date" = (SELECT MAX("Date") FROM nmf_spotify_coverage)
    GROUP BY "Artist"
    ORDER BY count DESC
    """
    df = pd.read_sql(query, engine)
    max_adds = df['count'].max()
    most_added_artists = df[df['count'] == max_adds]['Artist'].tolist()
    
    if len(most_added_artists) > 1:
        artist_names = " & ".join(most_added_artists[:-1]) + " and " + most_added_artists[-1]
    else:
        artist_names = most_added_artists[0]
    
    return artist_names, max_adds

def get_highest_reach(engine):
    query = """
    WITH LatestDate AS (
        SELECT MAX("Date") AS max_date FROM nmf_spotify_coverage
    ), ArtistFollowers AS (
        SELECT "Artist", SUM("Followers") AS total_followers
        FROM nmf_spotify_coverage, LatestDate
        WHERE "Date" = LatestDate.max_date
        GROUP BY "Artist"
    ), MaxFollowers AS (
        SELECT MAX(total_followers) AS max_followers
        FROM ArtistFollowers
    )
    SELECT af."Artist", af.total_followers
    FROM ArtistFollowers af
    JOIN MaxFollowers mf ON af.total_followers = mf.max_followers;
    """
    
    # Execute the query and fetch the data into a DataFrame
    df = pd.read_sql_query(query, engine)
    
    # Extract artist names and followers count
    most_reach_artists = df['Artist'].tolist()
    max_followers = df['total_followers'].iloc[0] if not df.empty else 0
    
    # Format the artist names for display
    if len(most_reach_artists) > 1:
        artist_names_reach = ", ".join(most_reach_artists[:-1]) + " and " + most_reach_artists[-1]
    else:
        artist_names_reach = most_reach_artists[0] if most_reach_artists else "No artists"
    
    return artist_names_reach, max_followers

def highest_average_position(engine):
    query = """
    WITH LatestDate AS (
        SELECT MAX("Date") AS max_date FROM nmf_spotify_coverage
    ), AvgPosition AS (
        SELECT "Artist", AVG("Position") AS average_position
        FROM nmf_spotify_coverage
        WHERE "Date" = (SELECT max_date FROM LatestDate)
        GROUP BY "Artist"
    ), BestAvgPosition AS (
        SELECT "Artist", average_position
        FROM AvgPosition
        ORDER BY average_position ASC
        LIMIT 1
    )
    SELECT * FROM BestAvgPosition;
    """
    
    # Execute the query
    df = pd.read_sql_query(query, engine)
    
    # Assuming df will have exactly one row as per the query's LIMIT 1
    if not df.empty:
        best_avg_playlist_position_by_artist = df.iloc[0]['Artist']
        best_avg = df.iloc[0]['average_position']
    else:
        best_avg_playlist_position_by_artist = "N/A"
        best_avg = None

    return best_avg_playlist_position_by_artist, best_avg

# Function to fetch unique dates from the database
@st.cache_data
def fetch_unique_dates():
    query = "SELECT DISTINCT \"Date\" FROM nmf_spotify_coverage ORDER BY \"Date\" DESC"
    unique_dates_df = pd.read_sql_query(query, engine)

    # Convert the 'Date' column to datetime using the known format 'YYYY-MM-DD'
    # 'errors='coerce'' will handle any parsing errors by converting them to NaT, which can then be filtered out
    unique_dates_df['Date'] = pd.to_datetime(unique_dates_df['Date'], format='%Y-%m-%d', errors='coerce')
    
    # Filter out any rows where the date could not be parsed
    unique_dates_df = unique_dates_df.dropna(subset=['Date'])

    # Convert dates to a more readable string format for display
    return unique_dates_df['Date'].dt.strftime("%A %d %B %Y").tolist()

# Function to load database data based on most recent 'Date'
@st.cache_data
def load_db_for_most_recent_date():
    query = """
    SELECT * FROM nmf_spotify_coverage
    WHERE "Date" = (SELECT MAX("Date") FROM nmf_spotify_coverage)
    """
    database_df = pd.read_sql_query(query, engine)
    return database_df

left_column, middle_column, right_column = st.columns(3)
left_column.image('images/nmf_logo.png')

todays_date = datetime.now().strftime("%A, %d %B, %Y")  # Format the date as Weekday, Day, Month, Year
right_column.write(todays_date)

st.title('New Release Playlist Adds:')
st.write('---')  # Add a visual separator
st.write('This site pulls all songs added to *New Music Friday AU & NZ*, and then checks to see if these songs have also been added to any key Australian editorial playlists.')  
st.write('For more info and the list of playlists that are tracked, check the About page.')  
st.write('---')  # Add a visual separator

col1, col2, col3 = st.columns([300, 0.5, 0.5])  

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)
##########################################################
##########################################################
# Retrieve Most Added
artist_names, max_adds = get_most_added_artist(engine)

# Set Most Added metric
with col1:
    st.metric(label="Most Added", value=f"{artist_names}", delta=f"Added to {max_adds} playlists")
    st.write("")
    
# Retrieve Highest Reach
artist_names_reach, max_followers = get_highest_reach(engine)

# Set Highest Reach metric
with col1:
    st.metric(label="Highest Reach", value=f"{artist_names_reach}", delta=f"{max_followers:,}", help='Total reach across playlist adds. Only based on the tracked playlists.', delta_color='normal')
    
# Retrieve Best Average By Artist
best_avg_playlist_position_by_artist, best_avg = highest_average_position(engine)

# Set Best Average Playlist Position
with col1:
    st.metric(label="Highest Average Playlist Position", 
              value=f"{best_avg_playlist_position_by_artist}", 
              delta=f"{best_avg:.0f}" if best_avg is not None else "N/A", 
              delta_color='normal', 
              help='Averages all positions across any new playlist additions')

########################################################## 
# # Display the data for the most recent date
df = load_db_for_most_recent_date()
# st.dataframe(df)

top_artists_reach = df.groupby('Artist').agg({
    'Followers': 'sum',
    'Playlist': lambda x: list(x.unique())  # Creates a list of unique playlists for each artist
})

# Sort the DataFrame based on 'Followers' while maintaining the whole DataFrame
sorted_top_artists_reach = top_artists_reach.sort_values(by='Followers', ascending=False)

# Select the top 5 artists while keeping all columns ('Followers' and 'Playlist')
results_with_playlist = sorted_top_artists_reach.head(5).copy()

# Calculate the 'Playlist_str' values using an intermediate step
playlist_str_series = results_with_playlist['Playlist'].apply(lambda x: ', '.join(x))

# Assign the calculated series to the DataFrame explicitly
results_with_playlist['Playlist_str'] = playlist_str_series

# Ensure 'Artist' is a column for Plotly (if 'Artist' was the index)
results_with_playlist = results_with_playlist.reset_index()

# Create a color scale
color_scale = [[0, 'lightsalmon'], [0.5, 'coral'], [1, 'orangered']]

# Create a bar chart using Plotly Express
fig = px.bar(results_with_playlist, x='Artist', y='Followers',
             text='Followers',
             hover_data=['Playlist_str'],  # Add 'Playlist_str' to hover data
             color='Followers',  # Assign color based on 'Followers' values
             color_continuous_scale=color_scale  # Use the custom color scale
             )

# Custom hover template to include Playlist information
fig.update_traces(hovertemplate='<b>%{x}</b><br>Reach: %{y:,}<br>Playlists: %{customdata[0]}')

# Display the exact number of followers on top of each bar and adjust other aesthetics
fig.update_traces(texttemplate='%{text:.3s}', textposition='inside')
fig.update_layout(
    xaxis_title="",
    yaxis_title="Total Reach",
    yaxis=dict(type='linear'),
    xaxis_tickangle=-30,
    plot_bgcolor='rgba(0,0,0)',
    margin=dict(t=100),
    title=dict(
        text='Top 5 Highest Reach',
        y=0.9,  # Adjust the title's position on the y-axis
        x=0.5,  # Center the title on the x-axis
        xanchor='center',  # Use the center of the title for x positioning
        yanchor='top'  # Anchor the title to the top of the layout
),
    coloraxis_showscale=False  # Optionally hide the color scale legend
    
    )
# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

##########################################################

##########################################################

st.write('- - - - - -')
st.subheader('Search Adds By Song:')

# Combine Artist & Title for the first dropdown box: 
df['Artist_Title'] = df['Artist'] + " - " + df['Title']
choices = df['Artist_Title'].unique()

# Sort the choices in alphabetical order before displaying in the dropdown
sorted_choices = sorted(choices, key=lambda x: x.lower())

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select a release:', sorted_choices)

# Filter DataFrame based on selection, then drop unnecessary columns for display
filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Order the filtered_df by 'Followers' in descending order
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Format the 'Followers' column to include commas for thousands
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=True, hide_index=True)

st.write('- - - - - -') 

st.subheader('Search Adds By Playlist:')

playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())

selected_playlist = st.selectbox('Select a Playlist:', playlist_choices, key='playlist_select')
# Filter DataFrame based on the selected playlist
filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# Display all songs in the selected playlist
st.dataframe(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True), hide_index=True, use_container_width=True)


# Cover Artists 
# Display the dictionary in the app
st.subheader('Cover Artists:')
cover_artist_df = pd.DataFrame(list(cover_artist_dict.items()), columns=['Playlist', 'Cover Artist'])
st.dataframe(cover_artist_df, use_container_width=True, hide_index=True)



st.write('- - - - - -') 

##########################################################


st.write("*Note: Cover artist may update before cover images*")


# # Playlist packshots
col1, col2, col3 = st.columns(3)

# Create a list of columns for easier access
cols = [col1, col2, col3]

# Total number of playlists
total_playlists = len(cover_art_dict)

# Iterate over your dictionary items
for index, (playlist_name, image_url) in enumerate(cover_art_dict.items()):
    # Get the artist name using the playlist name from the cover_artist_name_dict
    artist_name = cover_artist_dict.get(playlist_name, "Artist Unknown")
    
    # Check if this is the last image and if the total number is not divisible by 3, put it in col2
    if index == total_playlists - 1 and total_playlists % 3 != 0:
        col_index = 1  # Explicitly set to use col2
    else:
        # Calculate the column index in a round-robin fashion for all other cases
        col_index = index % 3
    
    # Display the image in the appropriate column with the artist name as the caption
    cols[col_index].image(image_url, caption=f"Cover Artist: {artist_name}", width=200)

st.write('- - - - - -') 

##########################################################

# Calculate the number of adds per playlist and sort for plotting
adds_per_playlist = df['Playlist'].value_counts().sort_values(ascending=True)

# Setting the style for the plot
plt.style.use('dark_background')  # Use a dark background style

# Plotting
fig, ax = plt.subplots(figsize=(6, 8))  # Adjust figure size for readability
adds_per_playlist.plot(kind='barh', ax=ax, color='#ab47bc')  # Adjusted to a lighter purple

# Customize tick parameters for better legibility
ax.tick_params(axis='x', colors='white', labelsize=12)  # Adjust x-axis ticks
ax.tick_params(axis='y', colors='white', labelsize=12)  # Adjust y-axis ticks
ax.set_title('Adds By Playlist', pad=70, weight='bold', color='white', fontsize=20, loc='left')

# Explicitly remove the grid
ax.grid(False)

# Move the x-axis label to the top
ax.xaxis.set_label_position('top')

ax.xaxis.tick_top()

# Set the x-axis label with custom formatting
ax.set_xlabel('No. of New Releases Added', labelpad=20, weight='light', color='white', fontsize=10, loc='left')
ax.set_xticks([10, 20, 30, 40, 50, 60, 70, 80])
ax.tick_params(top=False, left=False, right=False)
# Assume the rest of the code is written
ax.axvline(x=10, ymin=0.01, c='grey', alpha=0.4)

# Remove spines
for location in ['left', 'right', 'top', 'bottom']:
    ax.spines[location].set_visible(False)

st.pyplot(fig)


