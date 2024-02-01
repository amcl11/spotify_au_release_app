import pandas as pd
import numpy as np
import datetime as dt

# Read the HTML table into a DataFrame
df = pd.read_html('https://kworb.net/spotify/country/au_daily.html')[0]

# Get the current date minus 2 days to account for data lag
current_date_minus_2 = dt.datetime.now().date() - dt.timedelta(days=2)

# Add the current date as a new column to the DataFrame
df['DATE'] = current_date_minus_2

# Set the 'date' column as the index of the DataFrame and apply changes in place
df.set_index('DATE', inplace=True)

df = df.rename(columns={
    'Pos' : 'SPOTIFY_POS',
    'P+': 'SPOTIFY_MOVEMENT',
    'Artist and Title' : 'ARTIST_TITLE',
    'Days' : 'DAYS_IN_CHART',
    'Pk' : 'SPOTIFY_PEAK',
    '(x?)' : 'COUNT_AT_PEAK',
    'Streams' : 'SPOTIFY_DAILY_STREAMS',
    'Streams+' : 'SPOTIFY_DAILY_STREAMS_MOVEMENT',
    '7Day' : 'SPOTIFY_7DAY_STREAMS',
    '7Day+' : 'SPOTIFY_7DAY_STREAMS_MOVEMENT',
    'Total' : 'SPOTIFY_TOTAL_STREAMS',
})

# Remove "+" and ensure numeric conversion, allowing NaNs for non-numeric values
df['SPOTIFY_MOVEMENT'] = df['SPOTIFY_MOVEMENT'].str.replace('+', '', regex=False)
df['SPOTIFY_MOVEMENT'] = pd.to_numeric(df['SPOTIFY_MOVEMENT'], errors='coerce')


# Extract numeric values from 'COUNT_AT_PEAK'
df['COUNT_AT_PEAK'] = df['COUNT_AT_PEAK'].str.extract('(\d+)', expand=False)

# Convert to numeric, allowing NaNs to remain
df['COUNT_AT_PEAK'] = pd.to_numeric(df['COUNT_AT_PEAK'], errors='coerce')


df['ON_TOUR'] = np.nan
df['ACTIVE_PROMO'] = np.nan
df['ARIA_LW'] = np.nan
df['ARIA_TW'] = np.nan

# Specify the order of columns
columns_order = [
    'ARTIST_TITLE', 'SPOTIFY_POS', 'SPOTIFY_MOVEMENT',
    'DAYS_IN_CHART', 'SPOTIFY_PEAK', 'COUNT_AT_PEAK', 
    'SPOTIFY_DAILY_STREAMS', 'SPOTIFY_DAILY_STREAMS_MOVEMENT', 
    'SPOTIFY_7DAY_STREAMS', 'SPOTIFY_7DAY_STREAMS_MOVEMENT', 
    'SPOTIFY_TOTAL_STREAMS', 'ON_TOUR', 'ACTIVE_PROMO', 'ARIA_LW', 'ARIA_TW'
]

# Reorder the DataFrame according to the specified column order
df = df[columns_order]

# Create a mapping dictionary where keys are column names and values are desired data types
dtype_mapping = {
    'SPOTIFY_POS': 'Int64',  # Use nullable integer type
    'SPOTIFY_MOVEMENT': 'Int64',
    'DAYS_IN_CHART': 'Int64',
    'SPOTIFY_PEAK': 'Int64',
    'COUNT_AT_PEAK': 'Int64',
    'SPOTIFY_DAILY_STREAMS': 'Int64',
    'SPOTIFY_DAILY_STREAMS_MOVEMENT': 'Int64',
    'SPOTIFY_7DAY_STREAMS': 'Int64',
    'SPOTIFY_7DAY_STREAMS_MOVEMENT': 'Int64',
    'SPOTIFY_TOTAL_STREAMS': 'Int64',
    'ON_TOUR': 'Int64',  # Corrected to nullable integer
    'ACTIVE_PROMO': 'Int64',  # Corrected to nullable integer
    'ARIA_LW': 'Int64',  # Corrected to nullable integer
    'ARIA_TW': 'Int64',  # Corrected to nullable integer
    'ARTIST_TITLE': 'str',
}

# Apply the mapping to the DataFrame
df = df.astype(dtype_mapping)

# If DATE is your index and you want to convert it to datetime
df.index = pd.to_datetime(df.index)

# Load existing data from CSV
df_existing = pd.read_csv('main_chart_data.csv')

# Concatenate new data with existing data, avoiding duplicates
df_combined = pd.concat([df_existing, df], ignore_index=True).drop_duplicates(subset=['DATE', 'ARTIST_TITLE'])

# Save the combined DataFrame back to CSV
df_combined.to_csv('spotify_chart_data.csv', index=False)
