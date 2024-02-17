import pandas as pd
import numpy as np
import streamlit as st
import spotipy
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to fetch tracks from a Spotify playlist - Eg, fetch all tracks that were uploaded to New Music Friday on Friday morning
def fetch_playlist_tracks(sp, playlist_id):
    logging.info(f"Fetching playlist: {playlist_id}")
    track_ids = []
    artist_names = []
    track_names = []
    followers_count = 0

    try:
        playlist = sp.playlist(playlist_id)
        total_tracks = playlist['tracks']['total']
        followers_count = playlist['followers']['total']
    except spotipy.exceptions.SpotifyException as e:
        logging.error(f"An error occurred fetching playlist details: {e}")
        return track_ids, artist_names, track_names, followers_count

    offset = 0
    while offset < total_tracks:
        try:
            # Simplifying the fields parameter to potentially improve performance
            tracks = sp.playlist_items(playlist_id, offset=offset, fields='items(track(id,name,artists(name))),total', limit=100)
            items = tracks.get('items', [])
            if not items:  # Break the loop if no items are returned
                logging.info("No more tracks found, ending fetch.")
                break

            for item in items:
                track = item.get('track')
                if track:
                    track_ids.append(track.get('id'))
                    track_names.append(track.get('name'))
                    artist_names.append(', '.join([artist.get('name') for artist in track.get('artists', [])]))

            fetched_items = len(items)
            offset += fetched_items
            logging.info(f"Fetched {fetched_items} items, increasing offset to {offset}.")
        except spotipy.exceptions.SpotifyException as e:
            logging.error(f"An error occurred while fetching tracks: {e}")
            break  # Stop the loop on error

    return track_ids, artist_names, track_names, followers_count


def get_tracks_positions_in_playlists(sp, playlists_dict, track_ids):
    track_positions = {}
    playlist_follower_counts = {}  # Dictionary to store follower counts

    # Fetch the follower counts for all playlists first
    for playlist_name, playlist_id in playlists_dict.items():
        playlist = sp.playlist(playlist_id)
        playlist_follower_counts[playlist_name] = playlist['followers']['total']

    for track_id in track_ids:
        # Initialize an empty dict for each track_id
        track_positions[track_id] = {'positions': {}, 'artists': '', 'title': '', 'followers': {}}
        
        # Fetch track details (artist names and song title)
        track_details = sp.track(track_id)
        artists = ', '.join(artist['name'] for artist in track_details['artists'])
        title = track_details['name']
        
        # Store artist names and song title
        track_positions[track_id]['artists'] = artists
        track_positions[track_id]['title'] = title

    for playlist_name, playlist_id in playlists_dict.items():
        results = sp.playlist_tracks(playlist_id)
        position = 0

        while results:
            for item in results['items']:
                if item['track'] and item['track']['id'] in track_ids:
                    track_id = item['track']['id']
                    # Append position to the list for the corresponding track_id
                    if playlist_name not in track_positions[track_id]['positions']:
                        track_positions[track_id]['positions'][playlist_name] = []
                    track_positions[track_id]['positions'][playlist_name].append(position)
                    # Store the follower count for the playlist alongside positions
                    track_positions[track_id]['followers'][playlist_name] = playlist_follower_counts[playlist_name]
                position += 1
            results = sp.next(results) if results['next'] else None

    return track_positions


def fetch_and_display_playlist_info(sp, playlists_dict, playlist_id):
    """
    Fetches and displays information about tracks in a specific playlist and their positions in various playlists.

    This function performs multiple steps to gather and prepare data for display:
    1. Fetch playlist tracks: It calls a custom function `fetch_playlist_tracks` to retrieve track IDs, artist names, track names, and followers count for the specified playlist ID. This function is expected to communicate with the Spotify API and return the relevant data.

    2. Get track positions in playlists: Using another custom function `get_tracks_positions_in_playlists`, it obtains the positions of the fetched tracks across multiple playlists defined in `playlists_dict`. This involves querying the Spotify API for each track to see in which playlists they appear and at what positions.

    3. Prepare data for DataFrame creation: It then prepares the data for displaying by creating a list of dictionaries. Each dictionary corresponds to a track, containing the track's artist name, track title, and its position(s) in each playlist. For playlists where the track does not appear, empty strings are assigned as values. This step ensures that each track's data is structured in a way that can be easily converted into a pandas DataFrame.

        - For each track found in the `track_positions`, a new row is initialized with empty strings for each playlist (to handle tracks not appearing in some playlists).
        - The artist's name and track title are added to the row.
        - The track's position in each playlist (if any) is also added. Positions are adjusted to account for the zero-based indexing used by pandas (hence the `pos + 1` operation), and multiple positions are joined into a single string separated by commas.

    4. Convert list of dictionaries to DataFrame: Finally, the prepared list of dictionaries is converted into a pandas DataFrame. The DataFrame is structured with 'Artist' and 'Track' as the first two columns, followed by columns for each playlist. This DataFrame is suitable for displaying the gathered information in a tabular format, showing where and at what position each track appears across the specified playlists.

    Parameters:
    - sp: A Spotify client instance, used to communicate with the Spotify API.
    - playlists_dict: A dictionary mapping playlist names to their Spotify IDs. This is used to identify which playlists to check for track positions.
    - playlist_id: The Spotify ID of the playlist for which track information is being fetched.

    Returns:
    - df: A pandas DataFrame containing the fetched track information and their positions across multiple playlists.
    """
    
    # Fetch playlist tracks
    track_ids, artist_names, track_names, followers_count = fetch_playlist_tracks(sp, playlist_id)
    
    # Get track positions in playlists
    track_positions = get_tracks_positions_in_playlists(sp, playlists_dict, track_ids)

    # Prepare data for DataFrame creation
    data_for_df = []
    for track_id, details in track_positions.items():
        row = {playlist: np.nan for playlist in playlists_dict.keys()}  # Initialize row with np.nan for each playlist
        row['Artist'] = details['artists']
        row['Track'] = details['title']
        
        # Update row with track positions in playlists
        for playlist_name, positions in details['positions'].items():
            row[playlist_name] = ', '.join(str(pos + 1) for pos in positions)  # Adjust for zero indexing
            
        data_for_df.append(row)

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data_for_df, columns=['Artist', 'Track'] + list(playlists_dict.keys()))

    return df

# Fetch the initial data
@st.cache_data
def load_data(_sp, playlists_dict, playlist_id):
    print("Loading data...")
    track_ids, artist_names, track_names, _ = fetch_playlist_tracks(_sp, playlist_id)
    track_positions = get_tracks_positions_in_playlists(_sp, playlists_dict, track_ids)
    return track_positions

@st.cache_data
def load_data_and_create_df(_sp, playlists_dict, playlist_id):
    # Use your existing functions to load data
    track_positions = load_data(_sp, playlists_dict, playlist_id)
    
    # Initialize lists to hold data for DataFrame creation
    artists = []
    titles = []
    playlist_names = []
    positions = []
    followers = []

    # Iterate over the track_positions to aggregate data
    for track_id, details in track_positions.items():
        for playlist, pos_details in details['positions'].items():
            artists.append(details['artists'])
            titles.append(details['title'])
            playlist_names.append(playlist)
            positions.append(', '.join(map(str, pos_details)))
            followers.append(details['followers'][playlist])
    
    # Create a dictionary for DataFrame
    data = {
        'Artist': artists,
        'Title': titles,
        'Playlist': playlist_names,
        'Position': positions,
        'Followers': followers
    }

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)
    return df