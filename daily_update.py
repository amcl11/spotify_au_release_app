import pandas as pd
import numpy as np
import datetime as dt

# Read the HTML table into a DataFrame
df = pd.read_html('https://kworb.net/spotify/country/au_daily.html')[0]

# Get the current date minus 2 days to account for data lag
current_date_minus_2 = dt.datetime.now().date() - dt.timedelta(days=2)

# Add the current date as a new column to the DataFrame
df['DATE'] = current_date_minus_2

# Renaming columns 
df = df.rename(columns={
    'Pos': 'SPOTIFY_POS',
    'P+': 'SPOTIFY_MOVEMENT',
    'Artist and Title': 'ARTIST_TITLE',
    'Days': 'DAYS_IN_CHART',
    'Pk': 'SPOTIFY_PEAK',
    '(x?)': 'COUNT_AT_PEAK',
    'Streams': 'SPOTIFY_DAILY_STREAMS',
    'Streams+': 'SPOTIFY_DAILY_STREAMS_MOVEMENT',
    '7Day': 'SPOTIFY_7DAY_STREAMS',
    '7Day+': 'SPOTIFY_7DAY_STREAMS_MOVEMENT',
    'Total': 'SPOTIFY_TOTAL_STREAMS',
})

# Remove "+" and ensure numeric conversion, allowing NaNs for non-numeric values
df['SPOTIFY_MOVEMENT'] = df['SPOTIFY_MOVEMENT'].str.replace('+', '', regex=False).astype('Int64', errors='ignore')

# Extract and convert numeric values
df['COUNT_AT_PEAK'] = df['COUNT_AT_PEAK'].str.extract('(\d+)').astype('Int64', errors='ignore')

# Add some empty columns that will be used in the future
df['ON_TOUR'] = np.nan
df['ACTIVE_PROMO'] = np.nan
df['ARIA_LW'] = np.nan
df['ARIA_TW'] = np.nan

# Specifying column order and ensuring all necessary conversions
columns_order = [
    'DATE', 'ARTIST_TITLE', 'SPOTIFY_POS', 'SPOTIFY_MOVEMENT', 'DAYS_IN_CHART',
    'SPOTIFY_PEAK', 'COUNT_AT_PEAK', 'SPOTIFY_DAILY_STREAMS', 'SPOTIFY_DAILY_STREAMS_MOVEMENT',
    'SPOTIFY_7DAY_STREAMS', 'SPOTIFY_7DAY_STREAMS_MOVEMENT', 'SPOTIFY_TOTAL_STREAMS',
    'ON_TOUR', 'ACTIVE_PROMO', 'ARIA_LW', 'ARIA_TW'
]

# Apply the desired column order
df = df[columns_order]

# Load existing data from CSV
df_existing = pd.read_csv('cleaned_data/kworb.csv')

# Convert 'DATE' in df_existing to datetime, ensuring it matches the format in df
# This conversion should happen before attempting to access or manipulate the 'DATE' column
if 'DATE' not in df_existing.columns:
    raise KeyError("The 'DATE' column is missing from the existing DataFrame. Please ensure it is included in 'cleaned_data/kworb.csv'.")

df_existing['DATE'] = pd.to_datetime(df_existing['DATE'])

# Ensuring 'DATE' is a column in both DataFrames and properly formatted
df['DATE'] = pd.to_datetime(df['DATE'])

# Concatenate new data with existing data, avoiding duplicates
df_combined = pd.concat([df_existing, df], ignore_index=True).drop_duplicates(subset=['DATE', 'ARTIST_TITLE'])

# Save the combined DataFrame back to CSV
df_combined.to_csv('spotify_chart_data.csv', index=False)
print('CSV file has been updated')
