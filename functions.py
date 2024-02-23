import logging  # Import logging for error logging
import json
import re

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


# Function to validate the Spotify playlist link
def is_valid_spotify_link(link):
    # Regex pattern for Spotify playlist links
    pattern = r'https://open\.spotify\.com/playlist/[a-zA-Z0-9]{22}\?si=[a-zA-Z0-9]{16}'
    return re.match(pattern, link) is not None