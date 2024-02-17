import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json
import os
# Import your API credentials and custom functions
from api_credentials import client_id, client_secret
from functions import fetch_playlist_tracks, get_tracks_positions_in_playlists, load_data, fetch_and_display_playlist_info, load_data_and_create_df

# Set the title of the web application
st.title('New Release AU Playlist Adds:')
st.write(""" 
         
         Check *About* section for which playlists are tracked. 
        
         """)


# Initialize the Spotify client with your Spotify API client credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to display the table for a selected track
def display_table_for_selection(track_positions, selection):
    # Iterate through each track in the position data
    for track_id, details in track_positions.items():
        # Concatenate artist and track title for display
        artist_track = f"{details['artists']} - {details['title']}"
        # Check if the current track matches the user's selection
        if artist_track == selection:
            # Prepare data for displaying in the table
            combined_info = [
                (playlist, positions, details['followers'][playlist])
                for playlist, positions in details['positions'].items()
            ]
            # Sort the data by number of followers in descending order
            sorted_info = sorted(combined_info, key=lambda x: x[2], reverse=True)
            
            # Create a dictionary for the DataFrame
            table_data = {
                'Playlist': [info[0] for info in sorted_info],
                'Position': [', '.join(str(pos + 1) for pos in info[1]) for info in sorted_info],
                'Playlist Followers': [f"{info[2]:,}" for info in sorted_info]
            }

            # Convert the dictionary to a DataFrame and display it as a table
            df = pd.DataFrame(table_data)
            st.table(df)
            break  # Exit the loop after displaying the table for the selected track

# Load playlist data from a JSON file
with open('playlists.json', 'r') as file:
    playlists_dict = json.load(file)

# Load data for a specific playlist and prepare the dropdown selection options
playlist_id = '37i9dQZF1DWT2SPAYawYcO'  # Example: New Music Friday AU & NZ playlist ID
track_positions = load_data(sp, playlists_dict, playlist_id)
selections = [f"{details['artists']} - {details['title']}" for _, details in track_positions.items()]

# Create a dropdown for users to select an artist/track
selected_artist_track = st.selectbox('Select a New Release:', sorted(selections))

# Display the table for the selected artist/track
if selected_artist_track:
    display_table_for_selection(track_positions, selected_artist_track)


# Create a dropdown for users to select a playlist
selected_playlist = st.selectbox("Select a playlist to see Friday's additions:", sorted(playlists_dict.keys()))
selected_playlist_id = playlists_dict[selected_playlist]

df = load_data_and_create_df(sp, playlists_dict, playlist_id)

# Increase position by +1 to account for 0 index
df['Position'] = df['Position'].astype(int) + 1

# Filter the DataFrame to include only rows matching the selected playlist
filtered_df = df[df['Playlist'] == selected_playlist]

# Sort the filtered DataFrame by 'Position' in ascending order
filtered_df = filtered_df.sort_values(by='Position', ascending=True)

# Reset the index after sorting
filtered_df = filtered_df.reset_index(drop=True)

# Display the filtered DataFrame
st.table(filtered_df[['Artist', 'Title', 'Position']])












# User input section for requesting a new playlist to be tracked

user_input = st.text_input("If you want a playlist added. Submit the playlist ID here:")

# Button to submit user input
submit = st.button('Submit')

if submit:
    # Load existing data
    try:
        with open('user_input.json', 'r') as json_file:
            data = json.load(json_file)
            # Assuming the structure is {"user_inputs": ["id1", "id2"]}
            user_inputs = data.get("user_inputs", [])
    except FileNotFoundError:
        user_inputs = []

    # Append the new input
    user_inputs.append(user_input)

    # Write back to JSON with the updated list
    with open('user_input.json', 'w') as json_file:
        json.dump({"user_inputs": user_inputs}, json_file, indent=4)
    
    st.success('Submitted')
