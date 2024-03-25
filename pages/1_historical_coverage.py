import streamlit as st
import os
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
from datetime import datetime
import plotly.express as px

# Setup DATABASE_URL and engine
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

# Function to fetch unique dates from the database
@st.cache_data(ttl=3500, show_spinner='Fetching available dates...')
def fetch_unique_dates():
    query = "SELECT DISTINCT \"Date\" FROM nmf_spotify_coverage ORDER BY \"Date\" DESC"
    unique_dates_df = pd.read_sql_query(query, engine)

    # Convert the 'Date' column to datetime using the known format 'YYYY-MM-DD'
    # 'errors='coerce'' will handle any parsing errors by converting them to NaT, which can then be filtered out
    unique_dates_df['Date'] = pd.to_datetime(unique_dates_df['Date'], format='%Y-%m-%d', errors='coerce')
    
    # Filter out any rows where the date could not be parsed
    unique_dates_df = unique_dates_df.dropna(subset=['Date'])

    # Convert dates to a more readable string format for display
    return unique_dates_df['Date'].dt.strftime("%A %d %B %Y").tolist()

# Function to load database data based on selected date
# @st.cache_data - this was hingering updated triple j adds on Monday 
@st.cache_data(ttl=3500, show_spinner='Loading data...')
def load_db(selected_date_for_sql):
    query = "SELECT * FROM nmf_spotify_coverage WHERE \"Date\" = %s"
    database_df = pd.read_sql_query(query, engine, params=(selected_date_for_sql,))
    return database_df

st.subheader('Explore past release coverage:')

# Fetch unique dates and prepare them for the selectbox
unique_dates = fetch_unique_dates()

# User selects a date
selected_date_format = st.selectbox("Select a Friday", options=unique_dates)

# Convert selected date back to the original format for SQL query
selected_date_for_sql = datetime.strptime(selected_date_format, "%A %d %B %Y").strftime("%Y-%m-%d")

# Load data for the selected date
df = load_db(selected_date_for_sql)

# Filter dataframe to get the row with the "New Music Friday AU & NZ" playlist
nmf_image_series = df[df['Playlist'] == "New Music Friday AU & NZ"]['Image_URL']

# Extract the first image URL from the series
nmf_image_url = nmf_image_series.iloc[0] if not nmf_image_series.empty else None

col1, col2 = st.columns([3, 4])
# Display the image with a specific width
with col1:
    st.image(nmf_image_url, width=300)
    
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 15px;
}
</style>
""",
    unsafe_allow_html=True,
)

# Remove download and other buttons from all Dataframes
st.markdown(
                """
                <style>
                [data-testid="stElementToolbar"] {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

#######################
# HIGHEST REACH METRIC 
#######################

# Group by 'Title' and sum the 'Followers' for each title
title_followers = df.groupby('Title')['Followers'].sum()

# Find the maximum followers count for a title
max_followers = title_followers.max()

# Find the title(s) with the maximum followers count
title_with_max_followers = title_followers[title_followers == max_followers].index.tolist()

# Filter to find the artist for the top title
most_reach_title_df = df[df['Title'].isin(title_with_max_followers)].drop_duplicates(subset=['Title', 'Artist'])

# Sort artist names alphabetically
sorted_artists_reach = sorted(most_reach_title_df['Artist'].tolist())

# Display the metric first
with col2:
    label = ":grey[Highest Reach]"
    st.metric(label=label, value="", delta=f"{round(max_followers):,}", help='Total reach across AU playlist adds. Only based on the tracked playlists.', delta_color='normal')

# Prepare the HTML string for artist names with gap reduction, if there are multiple artists
if len(sorted_artists_reach) > 1:
    gap_reduction_html = "<div style='margin-top: -14px;'></div>"
    artist_names_html_reach = gap_reduction_html + "<br>".join(f"<span style='font-size: 95%; line-height: 1;'>{artist}</span>" for artist in sorted_artists_reach)
else:
    gap_reduction_html = "<div style='margin-top: -16px;'></div>"
    artist_names_html_reach = gap_reduction_html + f"<span style='font-size: 95%; line-height: 1;'>{sorted_artists_reach[0]}</span>"

# Use markdown to display artist names with reduced line spacing and smaller text
col2.markdown(artist_names_html_reach, unsafe_allow_html=True)

col2.write("")

#######################
# MOST ADDED METRIC
#######################

# Group by 'Title' and count the occurrences
title_counts = df.groupby('Title').size()

# Find the max number of adds
max_adds = title_counts.max()

# Find the title(s) with the max number of adds
most_added_titles = title_counts[title_counts == max_adds].index.tolist()

# Filter the original DataFrame to get the artist(s) for the most added title(s)
most_added_artists_df = df[df['Title'].isin(most_added_titles)].drop_duplicates(subset=['Title', 'Artist'])

# Sort artist names alphabetically
sorted_artists = sorted(most_added_artists_df['Artist'].tolist())

# Prepare the HTML string for artist names, with adjustments if there are multiple artists
if len(sorted_artists) > 1:
    # Join artist names with HTML line breaks and wrap in a span for styling, after sorting them alphabetically
    # Additionally, attempt to reduce the gap with a styled HTML block
    gap_reduction_html = "<div style='margin-top: -14px;'></div>"
    artist_names_html = gap_reduction_html + "<br>".join(f"<span style='font-size: 95%; line-height: 1;'>{artist}</span>" for artist in sorted_artists)
else:
    # For a single artist, adjust for gap and use the name without additional HTML
    gap_reduction_html = "<div style='margin-top: -16px;'></div>"
    artist_names_html = gap_reduction_html + f"<span style='font-size: 95%; line-height: 1;'>{sorted_artists[0]}</span>"

# Display the metric
with col2:
    label = ":grey[Most Added]"
    st.metric(label=label, value="", delta=f"Added to {max_adds} playlists")

    # Use markdown to display artist names with reduced line spacing and smaller text
    st.markdown(artist_names_html, unsafe_allow_html=True)

    col2.write("")
    col2.write("")

# ####################################
# # HIGHEST AVERAGE PLAYLIST POSITION 
# ####################################

# Group by 'Artist' and find the average 'Position'
avg_position_per_artist = df.groupby('Artist')['Position'].mean().reset_index(name='AvgPosition')

# Find the minimum average position
min_avg_position = avg_position_per_artist['AvgPosition'].min()

# Filter to get the artist(s) with the minimum average position
artists_with_lowest_avg_position = avg_position_per_artist[avg_position_per_artist['AvgPosition'] == min_avg_position]

# Prepare the HTML string for artist names with adjustments if there are multiple artists
if len(artists_with_lowest_avg_position) > 1:
    # Sort artist names alphabetically
    sorted_artists = sorted(artists_with_lowest_avg_position['Artist'].tolist())
    gap_reduction_html = "<div style='margin-top: -14px;'></div>"
    artist_names_html = gap_reduction_html + "<br>".join(f"<span style='font-size: 95%; line-height: 1;'>{artist}</span>" for artist in sorted_artists)
else:
    # For a single artist, adjust for gap and use the name without additional HTML
    gap_reduction_html = "<div style='margin-top: -16px;'></div>"
    artist_names_html = gap_reduction_html + f"<span style='font-size: 95%; line-height: 1;'>{artists_with_lowest_avg_position['Artist'].iloc[0]}</span>"

# Display the metric
with col2:
    label = ":grey[Highest Average Playlist Position]"
    st.metric(label=label, value="", delta=f"Average Position: {min_avg_position}")

    # Use markdown to display artist names with reduced line spacing and smaller text
    col2.markdown(artist_names_html, unsafe_allow_html=True)

########################################################## 
# TOP 5 HIGHEST REACH CHART
########################################################## 

st.write("---")
st.write(
    """
    <style>
        .my-text {
            font-size: 11px;
            font-family: monospace;
        }
    </style>
    <p class="my-text">Hover over chart to check playlist details</p>
    """,
    unsafe_allow_html=True,
)
# Use latest_friday_df from earlier in the code
top_artists_reach = df.groupby(['Artist', 'Title']).agg({
    'Followers': 'sum',
    'Playlist': lambda x: list(x.unique())  # Creates a list of unique playlists for each artist
})

# # Display the data for the most recent date
top_artists_reach = df.groupby(['Artist', 'Title']).agg({
    'Followers': 'sum',
    'Playlist': lambda x: list(x.unique())  # Creates a list of unique playlists for each artist
})

# Sort the DataFrame based on 'Followers' while maintaining the whole DataFrame
sorted_top_artists_reach = top_artists_reach.sort_values(by='Followers', ascending=False)

# Select the top 5 artists while keeping all columns ('Followers' and 'Playlist')
results_with_playlist = sorted_top_artists_reach.head(5).copy()

# Calculate the 'Playlist_str' values using an intermediate step
playlist_str_series = results_with_playlist['Playlist'].apply(lambda x: ', '.join(x))

# Assign the calculated series to the DataFrame explicitly
results_with_playlist['Playlist_str'] = playlist_str_series

# Ensure 'Artist' is a column for Plotly (if 'Artist' was the index)
results_with_playlist = results_with_playlist.reset_index()

# Create colour scale
color_scale = [[0, 'lightsalmon'], [0.5, 'coral'], [1, 'orangered']]

# Create bar chart with Plotly Express
fig = px.bar(results_with_playlist, x='Artist', y='Followers',
             text='Followers',
             hover_data=['Title', 'Playlist_str'],  # Add 'Playlist_str' to hover data
             color='Followers',  # Assign color based on 'Followers' values
             color_continuous_scale=color_scale  # Use the custom color scale
             )

# Custom hover template to include Playlist information
# Update hovertemplate to include 'Title'
fig.update_traces(hovertemplate='<b>%{x}</b> - %{customdata[0]}<br>Reach: %{y:,}<br>Playlists: %{customdata[1]}')

# Display the exact number of followers on top of each bar and adjust other aesthetics
fig.update_traces(texttemplate='%{text:.3s}', textposition='inside')

fig.update_layout(
    xaxis_title="",
    yaxis_title="Total Reach",
    yaxis=dict(type='linear'),
    xaxis_tickangle=-45,
    plot_bgcolor='rgba(0,0,0,0)',  # Set background color to transparent
    paper_bgcolor='#0E1117',  # Set the overall figure background color
    margin=dict(t=60, l=40, r=40, b=40),  # Adjust margin to make sure title fits
    title=dict(
        text='Top 5 Highest Reach',
        font=dict(
            family="Arial, sans-serif",
            size=18,
            color="white"
        ),
        y=0.9,  # Position title within the top margin of the plotting area
        x=0.5,  # Center the title on the x-axis
        xanchor='center',
        yanchor='top'
    ),
    coloraxis_showscale=False
)

fig.update_traces(texttemplate='%{text:.3s}', textposition='inside')
fig.update_layout(
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    showlegend=False  # Optionally hide the legend if not needed
)

# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

########################
# SEARCH ADDS BY SONG
########################

st.subheader('Search Adds By Song:')

# Combine Artist & Title for the first dropdown box: 
# Use latest_friday_df from earlier in the code

# Filter out rows where either 'Artist' or 'Title' is null for dropdown creation
filtered_df_for_artist_title = df.dropna(subset=['Artist', 'Title'])

# Temporarily create 'Artist_Title' in the filtered dataframe for dropdown options
filtered_df_for_artist_title['Artist_Title'] = filtered_df_for_artist_title['Artist'] + " - " + filtered_df_for_artist_title['Title']

# Ensure unique values and sort them for the dropdown
choices = filtered_df_for_artist_title['Artist_Title'].unique()
sorted_choices = sorted(choices, key=lambda x: x.lower())

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select Release:', sorted_choices)

# Add 'Artist_Title' to the original dataframe for filtering based on the dropdown selection
df['Artist_Title'] = df.apply(lambda row: f"{row['Artist']} - {row['Title']}" if pd.notnull(row['Artist']) and pd.notnull(row['Title']) else None, axis=1)

# Now filter the original DataFrame based on selection, this time it includes 'Artist_Title'
filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Continue with sorting and displaying the data as before
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Convert 'Followers' to integers to remove decimal points, then format as strings with commas
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].fillna(0).astype(int).apply(lambda x: f"{x:,}")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=False, hide_index=True)

###########################
# SEARCH ADDS BY PLAYLIST
###########################

st.write("")
st.subheader('Search Adds By Playlist:')

# Use latest_friday_df from earlier in the code
playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())

selected_playlist = st.selectbox('Select Playlist:', playlist_choices, key='playlist_select')

# Filter DataFrame based on the selected playlist
filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# Check if 'Artist' and 'Title' columns only contain None values
if filtered_playlist_df[['Artist', 'Title']].isnull().all(axis=None):
    st.markdown(f"<span style='color: #FAFAFA;'>No New Releases added to <span style='color: salmon;'>**{selected_playlist}**</span> that were also added to NMF AU & NZ</span>", unsafe_allow_html=True)

else:
    sorted_df = filtered_playlist_df.sort_values(by='Position', ascending=True)
    # Clean the DataFrame to replace None with 'N/A' for display
    sorted_df[['Artist', 'Title', 'Position']] = sorted_df[['Artist', 'Title', 'Position']].fillna('N/A')
    st.data_editor(
        data=sorted_df[['Artist', 'Title', 'Position']],
        disabled=True,  # Ensures data cannot be edited
        use_container_width=False,  
        column_config={
            "Artist": {"width": 150},  # Set tighter width
            "Title": {"width": 120},   # Set width
            "Position": {"width": 58}
        },
        hide_index=True
    )

######### BUILDING NEW GRAPH FEATURE - TOP PERFORMERS ######
st.write("-----")
st.subheader("Top Performers:")
st.write('Comparing the weekly top performing release (by reach) across the available weeks (23rd Feb onwards).')

# Define the caching function
@st.cache_data(ttl=259200, show_spinner="Fetching Top Performers...") #cache for 3 days 
def get_data(sql, _engine):
    return pd.read_sql(sql, _engine)

# SQL query
sql_query = """
WITH TotalFollowers AS (
  SELECT    
    "Date",
    "Artist",
    "Title",
    SUM("Followers") AS total_followers
  FROM nmf_spotify_coverage
  WHERE "Artist" IS NOT NULL AND "Title" IS NOT NULL AND "Followers" IS NOT NULL
  GROUP BY "Date", "Artist", "Title"
),
RankedArtists AS (
  SELECT
    "Date",
    "Artist",
    "Title",
    total_followers,
    RANK() OVER (PARTITION BY "Date" ORDER BY total_followers DESC) as rank
  FROM TotalFollowers
)
SELECT "Date", "Artist", "Title", total_followers
FROM RankedArtists
WHERE rank = 1
ORDER BY "Date";

"""

df = get_data(sql_query, engine)

df['Artist/Title'] = df['Artist'] + " - '" + df['Title'] + "'"
df['Date'] = pd.to_datetime(df['Date'])
df['formatted_followers'] = (df['total_followers'] / 1e6).map("{:.2f}m".format)

# Sort dataframe in descending order by 'total_followers'
df_sorted = df.sort_values(by='total_followers', ascending=False)

# Function to apply custom date formatting with suffix for the day
def custom_date_format(date):
    day = date.day
    day_with_suffix = f"{day}{suffix(day)}"
    formatted_date = date.strftime(f"{day_with_suffix} %B %Y")
    return formatted_date

def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

# Apply the custom date formatting function to your date column
df_sorted['formatted_date'] = df_sorted['Date'].apply(custom_date_format)

# Define a custom color scale with more subtle changes
# The numbers represent the relative positions of each color from 0 (start) to 1 (end)
custom_color_scale = [
    (0, 'rgb(230, 240, 255)'),  # Lighter blue
    (0.5, 'rgb(180, 210, 255)'),  # Medium blue
    (1, 'rgb(100, 150, 240)'),  # Darker blue
]

# Plotting with 'Artist/Title' on x-axis and total followers on y-axis
fig = px.bar(df_sorted, x='Artist/Title', y='total_followers', text='formatted_followers',
             title='',
             color='total_followers',
             color_continuous_scale=custom_color_scale,  # Use the custom color scale
             orientation='v',
             hover_data={'total_followers': ':,', 'formatted_date': True})  # Use formatted date

# Customize hover template to show 'Release Date'
fig.update_traces(hovertemplate='Release Date: %{customdata[0]}<extra></extra>')

# Move the text above the bars
fig.update_traces(textposition='outside')

# Calculate maximum value of 'total_followers' and add a buffer
max_value = df_sorted['total_followers'].max()  
buffer = max_value * 0.25  #buffer



fig.update_layout(
    yaxis=dict(
        title='Total Playlist Reach',
        # Define the range with a narrower lower bound or a higher upper bound
        range=[-max_value * 0.05, max_value * 1.10],  # The negative lower bound can give more "room" at the bottom
    ),
    xaxis_tickangle=30,
    xaxis_title='',
    showlegend=False,
    coloraxis_showscale=False,  # This hides the color scale bar
)

# # Update the layout with the new y-axis range
# fig.update_layout(
#     yaxis=dict(
#         title='Total Playlist Reach',
#         range=[0, max_value + buffer]  # Set the range from 0 to max value plus buffer
#     ),
#     xaxis_tickangle=35,
#     xaxis_title='',
#     showlegend=False,
#     coloraxis_showscale=False  # This hides the color scale bar
# )

# Display the plot, ensuring it takes up the full container width / removes display bar 
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})




    


