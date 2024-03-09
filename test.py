import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import os

# Configure logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting script execution")
print("Starting script execution")

# CLIENT_ID = os.getenv('CLIENT_ID')
# CLIENT_SECRET = os.getenv('CLIENT_SECRET')

CLIENT_ID = '8784eaf200a34094a36bacc773013d99'
CLIENT_SECRET = '7a8875d222bc4ec58463d29de92de13e'

if CLIENT_ID is None or CLIENT_SECRET is None:
    logging.error("CLIENT_ID or CLIENT_SECRET is None. Please check your environment variables.")
    print("CLIENT_ID or CLIENT_SECRET is None. Please check your environment variables.")
    exit()

# Initialize the Spotify client with a timeout (e.g., 10 seconds)
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, cache_handler=None)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10)
    logging.info("Spotify client initialized successfully")
    print("Spotify client initialized successfully")
except Exception as e:
    logging.error(f"Error initializing Spotify client: {e}")
    print(f"Error initializing Spotify client: {e}")
    exit()

playlist_id = '37i9dQZF1DWT2SPAYawYcO'

try:
    logging.info(f"Attempting to fetch tracks from playlist ID: {playlist_id}")
    results = sp.playlist_tracks(playlist_id, limit=1)
    
    if results and results['items']:
        track = results['items'][0]['track']
        logging.info(f"Successfully fetched first track: {track['name']} by {track['artists'][0]['name']}")
        print(f"Successfully fetched first track: {track['name']} by {track['artists'][0]['name']}")
    else:
        logging.warning("No tracks found in the playlist or unable to fetch tracks.")
        print("No tracks found in the playlist or unable to fetch tracks.")
except spotipy.exceptions.SpotifyException as e:
    if e.http_status == 429:
        retry_after = e.headers.get('Retry-After', 1)  # Default to 1 second if header missing
        logging.error(f"Hit rate limit. Retry after {retry_after} seconds")
        print(f"Hit rate limit. Retry after {retry_after} seconds")
    else:
        logging.error(f"Spotify API error: {e}")
        print(f"Spotify API error: {e}")
except Exception as e:
    logging.error(f"General exception occurred: {e}", exc_info=True)
    print(f"General exception occurred: {e}")
exit() # Ensure to exit or handle appropriately in case of failure
