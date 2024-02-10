# This function is designed to find the position of a specific track within a Spotify playlist. 
# It requires the Spotify API credentials (`client_id`, `client_secret`, and `redirect_uri`), a `playlist_id`, and a `track_id` to operate.

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_tracks_positions_in_playlists(client_id, client_secret, redirect_uri, playlists_dict, track_ids):
    scope = 'playlist-read-private'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))
    track_positions = {track_id: {} for track_id in track_ids}  # Dictionary to store positions

    for playlist_name, playlist_id in playlists_dict.items():
        results = sp.playlist_tracks(playlist_id)
        position = 0  # Reset position for each playlist

        while results:
            for item in results['items']:
                if item['track'] and item['track']['id'] in track_ids:
                    track_id = item['track']['id']
                    # Store the position in the corresponding dictionary
                    if playlist_id not in track_positions[track_id]:
                        track_positions[track_id][playlist_name] = []
                    track_positions[track_id][playlist_name].append(position)
                position += 1  # Increment position counter
            results = sp.next(results) if results['next'] else None

    return track_positions
