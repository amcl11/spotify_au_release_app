import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Function to fetch unique dates from the database
@st.cache_data
def fetch_unique_dates():
    conn = sqlite3.connect('spotify_nmf_data.db')
    query = "SELECT DISTINCT Date FROM nmf_spotify_coverage ORDER BY Date DESC"
    unique_dates_df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert the 'Date' column to datetime using the known format 'YYYY-MM-DD'
    # 'errors='coerce'' will handle any parsing errors by converting them to NaT, which can then be filtered out
    unique_dates_df['Date'] = pd.to_datetime(unique_dates_df['Date'], format='%Y-%m-%d', errors='coerce')
    
    # Filter out any rows where the date could not be parsed
    unique_dates_df = unique_dates_df.dropna(subset=['Date'])

    # Convert dates to a more readable string format for display
    return unique_dates_df['Date'].dt.strftime("%A %d %B %Y").tolist()


# Function to load database data based on selected date
@st.cache_data
def load_db(selected_date_for_sql):
    conn = sqlite3.connect('spotify_nmf_data.db')
    query = "SELECT * FROM nmf_spotify_coverage WHERE Date = ?"
    database_df = pd.read_sql_query(query, conn, params=[selected_date_for_sql])
    conn.close()
    return database_df

st.subheader('Select a previous Friday to explore past coverage...')

# Fetch unique dates and prepare them for the selectbox
unique_dates = fetch_unique_dates()

st.write('- - - - - -')

# Let the user select a date
selected_date_format = st.selectbox("Select a Friday", options=unique_dates)

# Convert the selected date back to the original format for SQL query
selected_date_for_sql = datetime.strptime(selected_date_format, "%A %d %B %Y").strftime("%Y-%m-%d")

# Load the data for the selected date
df = load_db(selected_date_for_sql)

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

