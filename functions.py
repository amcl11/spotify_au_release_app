import pandas as pd
import streamlit as st

# Function to fetch tracks from a Spotify playlist - Eg, fetch all tracks that were uploaded to New Music Friday on Friday morning
def fetch_playlist_tracks(sp, playlist_id):
    track_ids = []
    artist_names = []
    track_names = []

    playlist = sp.playlist(playlist_id)
    total_tracks = playlist['tracks']['total']

    offset = 0
    while offset < total_tracks:
        tracks = sp.playlist_items(playlist_id, offset=offset,
                                   fields='items.track.id,items.track.name,items.track.artists.name,total')
        
        for item in tracks['items']:
            track = item['track']
            if track:
                track_ids.append(track['id'])
                track_names.append(track['name'])
                artist_names.append(track['artists'][0]['name'])

        offset += len(tracks['items'])

    followers_count = playlist['followers']['total']

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

        df = df.append(row, ignore_index=True)

    return df

# Fetch the initial data
@st.cache_data
def load_data(_sp, playlists_dict, playlist_id):
    track_ids, artist_names, track_names, _ = fetch_playlist_tracks(_sp, playlist_id)
    track_positions = get_tracks_positions_in_playlists(_sp, playlists_dict, track_ids)
    return track_positions