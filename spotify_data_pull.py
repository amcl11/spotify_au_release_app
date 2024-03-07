# Import necessary libraries
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from functions import get_playlist_tracks_and_artists, find_tracks_positions_in_playlists
import json
import re
import logging 

# Use Streamlit's st.secrets to get the secret values
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# Load list of playlists from JSON file
with open('playlists.json', 'r') as file:
    playlists_dict = json.load(file)

# Initialise the Spotify client with client credentials for public data access
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Configure logging to file
logging.basicConfig(filename='log.txt', level=logging.INFO,  
                    format='%(asctime)s - %(levelname)s - %(message)s')

# New Music Friday AU & NZ playlist 
playlist_id = '37i9dQZF1DWT2SPAYawYcO'

print('Fetching Spotify data...')
# Fetches track names and artist names from New Music Friday AU & NZ
# Returns a list of tuples, each containing a track name and concatenated artist names.
# Example, [('Foam', 'Royel Otis'),('One More Night', 'KUČKA, Flume')]
track_details = get_playlist_tracks_and_artists(sp, playlist_id)

# Uses`track_details` from above and `playlists_dict' (loaded JSON file)
# Finds the positions of each track in multiple playlists

track_positions = find_tracks_positions_in_playlists(sp, track_details, playlists_dict)

# Fetching playlist follower counts
# Dictionary to store follower counts
playlist_followers = {}

# Fetching follower counts
for playlist_name, playlist_id in playlists_dict.items():
    playlist = sp.playlist(playlist_id)
    follower_count = playlist['followers']['total']
    playlist_followers[playlist_name] = follower_count
    
logging.info("Playlist followers data fetched successfully")

# Create and save fetched data as a DataFrame
rows = []

for track_id, track_info in track_positions.items():
    artist_name = track_info['artist_name']
    track_name = track_info['track_name']
    for playlist_info in track_info['playlists']:
        playlist_name = playlist_info['playlist']
        position = playlist_info['position']
        # Fetch the follower count using the playlist name
        followers = playlist_followers.get(playlist_name, 0)  # Default to 0 if playlist not found
        rows.append({
            'Artist': artist_name,
            'Title': track_name,
            'Playlist': playlist_name,
            'Position': position,
            'Followers': followers
        })

# Convert the list of rows into a DataFrame
df = pd.DataFrame(rows)

df.to_csv('streamlit.csv', index=False)
logging.info("DataFrame created and exported successfully ")

# Start collecting data for the Cover Art and Cover Artist info
#Fetch Playlist image URLs
cover_art_dict = {}

for playlist_name, playlist_id in playlists_dict.items():

    playlist_data = sp.playlist(playlist_id)

    # Fetching playlist cover image URL
    cover_image_url = playlist_data['images'][0]['url'] if playlist_data['images'] else 'No image available'

    # append to dictionary 
    cover_art_dict[playlist_name] = cover_image_url
logging.info("Cover image URLs returned successfuly")

# Fetch cover artist details 
# Initialise a dictionary to store playlist name and playlist cover artist details 
cover_artist_dict = {}

for playlist_name, playlist_id in playlists_dict.items():
    # Fetch playlist data from Spotify
    playlist = sp.playlist(playlist_id)

    # Extract the required information
    playlist_description = playlist.get('description', 'No description available')

    # Use regex for case-insensitive search for 'Cover: ' and extract the cover artist name
    match = re.search(r'cover:\s*(.*?)$', playlist_description, re.IGNORECASE)
    if match:
        cover_artist = match.group(1)  # Extract the matched artist name

        # Add to the dictionary only if the cover artist is meaningful (not 'No cover artist found')
        if cover_artist.strip().lower() != "no cover artist found":
            cover_artist_dict[playlist_name] = cover_artist
logging.info("Cover artist details returned successfully  ")


#Remove Image URLs from `cover_art_dict` that don't have a Cover Artist. Only Cover Art featuring an artist is useful. 
# Create a new dictionary that will only include matching keys
filtered_cover_art_dict = {}

# Loop through the cover_art_dict
for playlist_name in cover_art_dict:
    # Check if the current key also exists in cover_artist_dict
    if playlist_name in cover_artist_dict:
        # Add it to the new dictionary
        filtered_cover_art_dict[playlist_name] = cover_art_dict[playlist_name]
logging.info("Non-cover artist covers removed successfully")

# Save both Cover dictionaries to a single JOSN file for later import use into main.py.
data = {
    'filtered_cover_art_dict': filtered_cover_art_dict,
    'cover_artist_dict': cover_artist_dict
}

# Write the combined dictionary to a file
with open('cover_art_data.json', 'w') as f:
    json.dump(data, f, indent=4)
logging.info("Final 'cover_art_data.json' saved successfully ")
logging.info("Data pull complete.  ")