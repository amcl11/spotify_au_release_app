import pandas as pd
import datetime as dt

# Extract new data
df_new = pd.read_html('https://kworb.net/spotify/country/au_daily.html')[0]

# Get the current date minus 2 days to account for data lag
current_date_minus_2 = dt.datetime.now().date() - dt.timedelta(days=2)

# Add the current date as a new column to the DataFrame
df_new['DATE'] = current_date_minus_2

# Set the 'date' column as the index of the DataFrame and apply changes in place
df_new.set_index('DATE', inplace=True)

df = df_new.rename(columns={
    'Pos' : 'TW_SPOTIFY_POS',
    'P+': 'SPOTIFY_CHART_MOVEMENT',
    'Artist and Title' : 'ARTIST_TITLE',
    'Days' : 'DAYS_IN_CHART',
    'Pk' : 'SPOTIFY_PEAK',
    '(x?)' : 'COUNT_AT_PEAK',
    'Streams' : 'SPOTIFY_DAILY_STREAMS',
    'Streams+' : 'SPOTIFY_STREAMS_MOVEMENT',
    '7Day' : 'SPOTIFY_7DAY_STREAMS',
    '7Day+' : 'SPOTIFY_7DAY_STREAMS_MOVEMENT',
    'Total' : 'SPOTIFY_TOTAL_STREAMS',
})

df['SPOTIFY_CHART_MOVEMENT'] = df['SPOTIFY_CHART_MOVEMENT'].replace("=", "0")

# Load existing data from CSV
df_existing = pd.read_csv('spotify_chart_data.csv')

# Concatenate new data with existing data, avoiding duplicates
df_combined = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates(subset=['DATE', 'ARTIST_TITLE'])

# Save the combined DataFrame back to CSV
df_combined.to_csv('spotify_chart_data.csv', index=False)
