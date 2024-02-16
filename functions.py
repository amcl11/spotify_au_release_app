import pandas as pd
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
    # Fetch playlist tracks
    track_ids, artist_names, track_names, followers_count = fetch_playlist_tracks(sp, playlist_id)
    
    # Get track positions
    track_positions = get_tracks_positions_in_playlists(sp, playlists_dict, track_ids)

    # Create a DataFrame to hold all playlist names as columns
    playlist_names = list(playlists_dict.keys())
    df = pd.DataFrame(columns=['Artist', 'Track'] + playlist_names)

    # Populate the DataFrame with positions
    for track_id, details in track_positions.items():
        row = {name: '' for name in playlist_names}  # Initialize row with empty strings
        row['Artist'] = details['artists']
        row['Track'] = details['title']

        for playlist_name, positions in details['positions'].items():
            # Join positions if there are multiple, else just convert to string
            row[playlist_name] = ', '.join(str(pos + 1) for pos in positions)

        row_df = pd.DataFrame([row])
        df = pd.concat([df, row_df], ignore_index=True)

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