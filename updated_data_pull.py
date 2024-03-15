import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from functions import get_playlist_tracks_and_artists, find_tracks_positions_in_playlists
import json
import re
import logging 
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import psycopg2
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

def schedule():
    print(f"Automated Data Pull executed at {datetime.now(pytz.timezone('Australia/Sydney'))}")
    scheduler = BlockingScheduler(timezone="Australia/Sydney")
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=0, minute=1))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=0, minute=15))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=5, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=6, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=7, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=8, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=8, minute=15))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=8, minute=45))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=9, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=9, minute=30))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=9, minute=55))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=10, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=10, minute=10))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=10, minute=15))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=11, minute=00))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=12, minute=30))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=1))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=4))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=8))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=9))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=20))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=15, minute=30))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=16, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=17, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='fri', hour=22, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='sat', hour=6, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='sun', hour=6, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='mon', hour=6, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='tue', hour=6, minute=0))
    scheduler.add_job(data_pull, CronTrigger(day_of_week='wed', hour=9, minute=0))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

def data_pull():
    # data pull logic and database upload below

    # # Fetch credentials via environment variables
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    # Load list of playlists from JSON file
    with open('playlists.json', 'r') as file:
        playlists_dict = json.load(file)

    # Initialise the Spotify client with client credentials for public data access
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Configure logging to file
    logging.basicConfig(filename='log.txt', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%A %Y-%m-%d %H:%M:%S')  # Custom date format

    # New Music Friday AU & NZ playlist 
    playlist_id = '37i9dQZF1DWT2SPAYawYcO'

    print('Fetching Spotify data...')
    
    # Fetches track names and artist names from New Music Friday AU & NZ
    # Returns a list of tuples, each containing a track name and concatenated artist names.
    # Example, [('Foam', 'Royel Otis'),('One More Night', 'KUČKA, Flume')]
    track_details = get_playlist_tracks_and_artists(sp, playlist_id)
    print(f'Fetched {len(track_details)} track details from New Music Friday AU & NZ playlist.')
    
    # Uses`track_details` from above and `playlists_dict' (loaded JSON file)
    # Finds the positions of each track in multiple playlists
    track_positions = find_tracks_positions_in_playlists(sp, track_details, playlists_dict)
    print(f'Track positions in other playlists found for {len(track_positions)} tracks.')
    
    ###########################################
    ###########################################
    ###########################################
    # troubleshooting missing Get Popped! info...
    # file_name = 'track_positions.json'

    # try:
    #     with open(file_name, 'w') as file:
    #         json.dump(track_positions, file, indent=4)
    #     print(f"Track positions successfully exported to {file_name}")
    # except Exception as e:
    #     print(f"Error exporting track positions: {e}")  
    
    ###########################################
    ###########################################
    ###########################################
    
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

    for _, track_info in track_positions.items():
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
    # Get the unique values from the 'Playlist' column
    unique_playlists_in_df = df['Playlist'].unique()
    logging.info("Initial DataFrame created successfully ")
    logging.info(f'Unique Playlists In First DF: {unique_playlists_in_df}')

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

        # Define regex patterns
        # Case-insensitive 
        patterns = [
            r'cover:\s*(.*?)$',  # Pattern for "Cover: artist_name"
            r'\.\s*([^\.]+)$'    # Pattern for "sentence. artist_name", as a fallback
        ]

        cover_artist = None
        for pattern in patterns:
            match = re.search(pattern, playlist_description, re.IGNORECASE)
            if match:
                cover_artist = match.group(1).strip()
                if cover_artist and cover_artist.lower() != "no cover artist found":
                    cover_artist_dict[playlist_name] = cover_artist
                    break  # If a valid cover artist is found, stop looking through other patterns
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

    # Create variable for all cover_info data
    cover_info_data = {
        'filtered_cover_art_dict': filtered_cover_art_dict,
        'cover_artist_dict': cover_artist_dict
    }
    # logging.info("cover_info_data collected successfully. Details: %s", str(cover_info_data))

    cover_info_df = pd.DataFrame({
            'Playlist': list(cover_info_data['filtered_cover_art_dict'].keys()),
            'Cover Art URL': list(cover_info_data['filtered_cover_art_dict'].values()),
            'Featured Artist': list(cover_info_data['cover_artist_dict'].values())
        })
    unique_playlists = cover_info_df['Playlist'].unique().tolist()  # Convert to list for better readability in log
    logging.info("Unique playlists with cover art and artist details: %s", unique_playlists)
    
    todays_date = datetime.today()
    formatted_date = todays_date.strftime('%Y-%m-%d') # Format the date as a string in 'YYYY-MM-DD' format

    df.insert(0, 'Date', formatted_date)
    cover_info_df.insert(0, 'Date', formatted_date)

    merged_df = pd.merge(df, cover_info_df, on=['Date', 'Playlist'], how='outer')

    # rename columns to match DB 
    rename_mapping = {
        'Date': 'Date',
        'Artist' : 'Artist',
        'Title' : 'Title',
        'Playlist' : 'Playlist',
        'Position' : 'Position',
        'Followers' : 'Followers',
        'Cover Art URL' : 'Image_URL',
        'Featured Artist' : 'Cover_Artist'
        }

    merged_df.rename(columns=rename_mapping, inplace=True)

    # Convert the DataFrame 'Date' column to datetime and format it as needed
    merged_df['Date'] = pd.to_datetime(merged_df['Date']).dt.strftime('%Y-%m-%d')


    # Database upload
    ####################
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        # logging.info("Updated DATABASE_URL to use 'postgresql://'")

    logging.info("Connecting to db.")
    engine = create_engine(DATABASE_URL)

    # Calculating the upload date
    now = datetime.now()
    weekday = now.weekday()

    if weekday == 5: # Saturday
        days_to_subtract = 1
    elif weekday == 6: # Sunday
        days_to_subtract = 2
    elif weekday < 4: # Monday (0) to Thursday (3)
        days_to_subtract = weekday + 3 # Adjust to get to the last Friday
    else: # Friday
        days_to_subtract = 0

    upload_date = (now - timedelta(days=days_to_subtract)).strftime('%Y-%m-%d')
    logging.info(f"Upload date determined as: {upload_date}")


    with engine.connect() as conn:
        with conn.begin() as trans:
            try:
                logging.info(f"Attempting to delete existing records for date {upload_date}.")
                result = conn.execute(
                text("""DELETE FROM public.nmf_spotify_coverage WHERE "Date" = :date"""),
                date=upload_date)
                
                logging.info(f"Deleted {result.rowcount} existing records for date {upload_date}.")
                logging.info("Inserting new data.")
                # Ensure 'merged_df' has the correct 'Date' set to 'upload_date' before insertion
                merged_df['Date'] = upload_date
                
                # logging.info(f"Preview of merged_df before insertion:\n{merged_df.head()}")
                
                # Count amount of new rows being insterted for comparison to deletion 
                inserted_row_count = len(merged_df)    
                merged_df.to_sql('nmf_spotify_coverage', con=engine, if_exists='append', index=False)
            
                logging.info(f"Inserted {inserted_row_count} new records successfully.")
                trans.commit()
                logging.info("Database transaction committed.")
            except Exception as e:
                trans.rollback()
                logging.error(f"An error occurred: {e}")
                raise

    logging.info("Database upload completed.")
    
    pass

if __name__ == "__main__":
    schedule()