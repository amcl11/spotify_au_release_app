import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
from api_credentials import client_id, client_secret
from functions import fetch_playlist_tracks, get_tracks_positions_in_playlists, load_data

# Title of the web application
st.title('Spotify New Release Playlists & Positions:')

# Load playlists from JSON file
with open('playlists.json', 'r') as file:
    playlists_dict = json.load(file)

# Initialize the Spotify client with client credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Function to display the table for a selected artist/track
def display_table_for_selection(track_positions, selection):
    # Find the artist/track in the data
    for track_id, details in track_positions.items():
        artist_track = f"{details['artists']} - {details['title']}"
        if artist_track == selection:
            # Prepare the table data
            playlist_info = details['positions']
            table_data = {
                'Playlist': list(playlist_info.keys()),
                'Position': [', '.join(str(pos + 1) for pos in positions) for positions in playlist_info.values()]
            }
            df = pd.DataFrame(table_data)
            st.table(df)
            break

# Load playlist data and prepare selections
playlists_dict = st.session_state.get('playlists_dict')
if not playlists_dict:
    with open('playlists.json', 'r') as file:
        playlists_dict = json.load(file)
    st.session_state['playlists_dict'] = playlists_dict

playlist_id = '37i9dQZF1DWT2SPAYawYcO'  # New Music Friday AU & NZ playlist ID
track_positions = load_data(sp, playlists_dict, playlist_id)
selections = [f"{details['artists']} - {details['title']}" for _, details in track_positions.items()]

# Dropdown for artist/track selection
selected_artist_track = st.selectbox('Select a New Release:', selections)

# Display the table for the selected artist/track
if selected_artist_track:
    display_table_for_selection(track_positions, selected_artist_track)
