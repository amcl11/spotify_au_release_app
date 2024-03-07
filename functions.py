# Import necessary libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
import re
from time import sleep
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch API key and secret key from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Initialise the Spotify client with client credentials for public data access
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# # Use Streamlit's st.secrets to get the secret values
# CLIENT_ID = st.secrets["CLIENT_ID"]
# CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# Load list of playlists from JSON file
with open('playlists.json', 'r') as file:
    playlists_dict = json.load(file)


def get_playlist_tracks_and_artists(sp, playlist_id):
    """
    Fetches track names and artist names from a Spotify playlist.

    Args:
    - sp (spotipy.Spotify): An authenticated instance of the Spotipy client.
    - playlist_id (str): The Spotify ID of the playlist from which to fetch tracks.

    Returns:
    - list: A list of tuples, each containing a track name and concatenated artist names.
    """    
    track_details = []
    try:
        # Request specific fields to minimize data transfer
        results = sp.playlist_items(playlist_id, fields="items.track(name,artists.name),next")
        
        # Iterate through all pages of results
        while results:
            tracks = results['items']
            for item in tracks:
                track = item['track']
                if track:  # Ensure the track information exists
                    track_name = track['name']
                    artist_names = ', '.join(artist['name'] for artist in track['artists'])
                    track_details.append((track_name, artist_names))
            
            # Fetch the next page of results, if available
            results = sp.next(results) if results['next'] else None

    except Exception as e:
        logging.error(f"Failed to fetch tracks from playlist {playlist_id}: {e}")
    
    return track_details

def find_tracks_positions_in_playlists(sp, track_details, playlists_dict):
    """
    Finds the positions of specified tracks in multiple playlists, including their names and artist names.

    Args:
    - sp (spotipy.Spotify): An authenticated instance of the Spotipy client.
    - track_details (list): A list of tuples with track names and their corresponding artist names.
    - playlists_dict (dict): A dictionary mapping playlist names to their Spotify IDs.

    Returns:
    - dict: A dictionary with track names and artist names as keys, detailing their presence and positions in playlists.
    """
    track_positions = {}

    # Prepare a dictionary mapping track names and artist names to their details
    track_info_dict = {(name, artist): {'track_name': name, 'artist_name': artist, 'playlists': []} for name, artist in track_details}

    for playlist_name, playlist_id in playlists_dict.items():
        try:
            # Fetch tracks and their artists from each playlist
            playlist_tracks = get_playlist_tracks_and_artists(sp, playlist_id)
            for position, (track_name, artist_names) in enumerate(playlist_tracks, start=1):
                key = (track_name, artist_names)
                if key in track_info_dict:
                    # Record the playlist and position for each matching track
                    track_info_dict[key]['playlists'].append({
                        'playlist': playlist_name,
                        'position': position
                    })
        except Exception as e:
            print(f"Error processing playlist {playlist_name}: {e}")

    # Format the output dictionary to include track names, artist names, and their playlist positions
    track_positions = {f"{name} - {artist}": info for (name, artist), info in track_info_dict.items()}

    return track_positions


# Code for the 'about' section' - User input for a Playlist ID submission 

def save_user_input(playlist_id, file_path='user_input.json'):
    # Try to read the existing data, if the file does not exist, create an empty structure
    try:
        with open(file_path, 'r') as file:
            current_data = json.load(file)
    except FileNotFoundError:
        current_data = {"submitted_playlists": []}
    
    # Check if 'submitted_playlists' key exists, if not, create it
    if 'submitted_playlists' not in current_data:
        current_data['submitted_playlists'] = []
    
    # Add the new playlist ID to the list
    current_data['submitted_playlists'].append(playlist_id)
    
    # Write the updated data back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(current_data, file, indent=4)


# Function to validate the Spotify playlist link for the Submission form 
def is_valid_spotify_link(link):
    # Regex pattern for Spotify playlist links
    pattern = r'https://open\.spotify\.com/playlist/[a-zA-Z0-9]{22}\?si=[a-zA-Z0-9]{16}'
    return re.match(pattern, link) is not None


def is_correct_track(track, artist, title):
    return track['artists'][0]['name'].lower() == artist.lower() and track['name'].lower() == title.lower()

def update_popularity(artist_title):
    artist, title = artist_title.split(' - ', 1)
    try:
        results = sp.search(q='artist:' + artist + ' track:' + title, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            if is_correct_track(track, artist, title):
                return track['popularity']
            else:
                logging.warning(f"No accurate match found for {artist_title}")
        else:
            logging.info(f"No results for {artist_title}")
    except Exception as e:
        logging.error(f"Error fetching data for {artist_title}: {e}")
        sleep(1)  # Simple backoff strategy
    return None  # Return None or a default value for missing/incorrect data

def apply_update_popularity(row):
    # Extract 'Artist_Title' from the row and call update_popularity
    return update_popularity(row['Artist_Title'])


# Function to check if the last entry in the CSV matches today's date
def is_latest_entry_today(csv_path, today_date):
    if os.path.exists(csv_path):
        # Read the last few lines of the file to find the latest date
        with open(csv_path, 'r') as file:
            last_line = None
            for last_line in (line for line in file if line.rstrip('\n')):
                pass
            if last_line:
                # Assuming the date is the first column
                last_date = last_line.split(',')[0]
                return last_date == today_date
    return False


# Function to load the JSON file into a DataFrame before merging and storing in SQL db
def load_json_to_dataframe(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Transform the nested dictionaries into a pandas DataFrame
    dataframe = pd.DataFrame({
        'Playlist': list(data['filtered_cover_art_dict'].keys()),
        'Cover Art URL': list(data['filtered_cover_art_dict'].values()),
        'Featured Artist': list(data['cover_artist_dict'].values())
    })
    
    return dataframe