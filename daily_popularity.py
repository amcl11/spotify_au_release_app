# Import necessary libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api_credentials import client_id, client_secret
import pandas as pd
from functions import apply_update_popularity, is_latest_entry_today
from datetime import date
import os

# Initialise the Spotify client with client credentials for public data access
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

df = pd.read_csv('streamlit.csv')

# Ensure the 'Artist_Title' column is created by concatenating 'Artist' and 'Title'
df['Artist_Title'] = df['Artist'] + ' - ' + df['Title']

# Drop duplicates based on 'Artist_Title' immediately to avoid unnecessary iterations
df = df.drop_duplicates(subset='Artist_Title', keep='first').reset_index(drop=True)

# Now, apply the function to each row and update the 'Popularity' column
# Assuming apply_update_popularity is your function to fetch or calculate popularity
df['Popularity'] = df.apply(lambda row: apply_update_popularity(row), axis=1)

# Sort by 'Popularity' in descending order and drop rows with NaN in 'Popularity'
df_sorted_cleaned = df.sort_values(by="Popularity", ascending=False).dropna(subset=['Popularity'])

# Select only the 'Artist_Title' and 'Popularity' columns
final_df = df_sorted_cleaned[['Artist_Title', 'Popularity']]

# Add a 'Date' column with today's date formatted as 'YYYY-MM-DD'
today_date = date.today().strftime('%Y-%m-%d')
final_df.insert(0, 'Date', today_date)

final_df = final_df.reset_index(drop=True)

# Display the top rows of the final DataFrame
final_df.head(10)

# Define the file path
csv_file_path = 'popularity_data/popularity_data.csv'  # The same generic file name for appending

# Check if today's data is already present
if not is_latest_entry_today(csv_file_path, today_date):
    # Proceed with appending if today's data is not already present
    file_exists = os.path.isfile(csv_file_path)
    # Append the DataFrame to the CSV file, without the header if the file already exists
    final_df.to_csv(csv_file_path, mode='a', index=False, header=not file_exists)
else:
    print("Today's data has already been appended. Skipping.")


