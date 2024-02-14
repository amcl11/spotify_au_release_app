def get_tracks_positions_in_playlists(sp, playlists_dict, track_ids):
    track_positions = {}
    
    for track_id in track_ids:
        # Initialize an empty dict for each track_id
        track_positions[track_id] = {'positions': {}, 'artists': '', 'title': ''}
        
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
                position += 1
            results = sp.next(results) if results['next'] else None

    return track_positions
