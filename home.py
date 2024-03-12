# Dependencies 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import plotly.express as px
from theme import set_theme
from sqlalchemy import create_engine, text
import os

# set_theme() # Backup option if config theme setting don't work

# Setup DATABASE_URL and engine
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)

##################################
# TITLE INFO
##################################
st.title('New Release Playlist Adds:')
left_column, middle_column, right_column = st.columns(3)
left_column.image('images/nmf_logo_transparent_background.png')

st.write('This site streamlines Friday morning playlist checking for those interested in New Release coverage on Spotify in Australia.')
st.write('All songs added to *New Music Friday AU & NZ* are fetched, and then checked against key AU editorial playlists.')  
st.write('For more info and the list of playlists that are tracked, check the About page.')  
st.write('---')  # Add a visual separator

##################################
# DISPLAY MOST RECENT FRIDAY DATE
##################################

# Get the current datetime
now = datetime.now()
# Determine the current day of the week (0=Monday, 6=Sunday)
weekday = now.weekday()

# Calculate the days to subtract to get the most recent Friday
days_to_subtract = (weekday - 4) % 7
most_recent_friday = now - timedelta(days=days_to_subtract)

# Create a custom function to format the day with the suffix
def add_suffix_to_day(day):
    return f"{day}{('th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th'))}"

# Format the most recent Friday date
day_with_suffix = add_suffix_to_day(most_recent_friday.day)
most_recent_friday_str = most_recent_friday.strftime(f"Release Date: {day_with_suffix} %B, %Y")

# Display the most recent Friday 
st.subheader(most_recent_friday_str)

############################################################################################
# MAIN FUNCTION TO LOAD LATEST FRIDAY DATA FOR HOME.PY - Cached for 58.33 mins (ttl=3500) 
############################################################################################

@st.cache_data(ttl=3500, show_spinner='Fetching New Releases...')
def load_db_for_most_recent_date():
    query = """
    SELECT * FROM nmf_spotify_coverage
    WHERE "Date" = (SELECT MAX("Date") FROM nmf_spotify_coverage)
    """
    latest_friday_df = pd.read_sql_query(query, engine)
    return latest_friday_df

# Main dataframe to use for home.py 
latest_friday_df = load_db_for_most_recent_date()

# Set columns for metrics 
col1, col2, col3 = st.columns([300, 0.5, 0.5])  

# Set metric text size
st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 18px;
}
</style>
""",
    unsafe_allow_html=True,
)

#######################
# HIGHEST REACH METRIC 
#######################

# Group by 'Title' and 'Artist', then sum the 'Followers' column
highest_reach = latest_friday_df.groupby(['Title', 'Artist'])['Followers'].sum().reset_index(name='Reach')

# Find the maximum reach
max_reach = highest_reach['Reach'].max()

# Filter to get the titles with the maximum reach
highest_reach_max = highest_reach[highest_reach['Reach'] == max_reach].reset_index(drop=True)

# Display the 'Highest Reach' title(s) and artist(s) as metrics in col1
for i in range(len(highest_reach_max)):
    title, artist, reach = highest_reach_max.iloc[i]['Title'], highest_reach_max.iloc[i]['Artist'], highest_reach_max.iloc[i]['Reach']
    with col1:
        st.metric(label="Highest Reach", value=f"{artist} - '{title}'", delta=f"{reach:0,}")
        st.write("")  # Adds space between metrics if there are multiple

#######################
# MOST ADDED METRIC
#######################

# Use latest_friday_df from earlier in the code
# Find the titles with the most entries
most_added = latest_friday_df.groupby(['Title', 'Artist']).size().reset_index(name='Count')

max_count = most_added['Count'].max()
most_added_max = most_added[most_added['Count'] == max_count].reset_index(drop=True)

# Display the most added title(s) and artist(s) as metrics in col1
for i in range(len(most_added_max)):
    title, artist = most_added_max.iloc[i]['Title'], most_added_max.iloc[i]['Artist']
    with col1:
        st.metric(label=f"Most Added", value=f"{artist} - '{title}'", delta=f"Added to {max_count} playlists")
        st.write("")  # Adds some space between metrics if there are multiple

#################################
# BEST AVERAGE PLAYLIST POSITION 
#################################

# Use latest_friday_df from earlier in the code
# Group by 'Title' and 'Artist', then find the average 'Position'
avg_position = latest_friday_df.groupby(['Title', 'Artist'])['Position'].mean().reset_index(name='AvgPosition')

# Find the minimum average position
min_avg_position = avg_position['AvgPosition'].min()

# Filter to get the titles and artists with the minimum average position
lowest_avg_position = avg_position[avg_position['AvgPosition'] == min_avg_position].reset_index(drop=True)

# Display the title(s) and artist(s) with the lowest average position as metrics in col1
for i in range(len(lowest_avg_position)):
    title, artist = lowest_avg_position.iloc[i]['Title'], lowest_avg_position.iloc[i]['Artist']
    with col1:
        # Using the title "Top Ranking" or similar since we're showing the lowest avg. position (which is best)
        st.metric(label="Best Average Playlist Position", value=f"{artist} - '{title}'", delta=f"Average Playlist Position: {round(min_avg_position)}")
        st.write("")  # Adds some space between metrics if there are multiple

########################################################## 
# TOP 5 HIGHEST REACH CHART
########################################################## 

# Use latest_friday_df from earlier in the code
top_artists_reach = latest_friday_df.groupby(['Artist', 'Title']).agg({
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

# Create a color scale
color_scale = [[0, 'lightsalmon'], [0.5, 'coral'], [1, 'orangered']]

# Create a bar chart using Plotly Express
fig = px.bar(results_with_playlist, x='Artist', y='Followers',
             text='Followers',
             hover_data=['Title', 'Playlist_str'],  # Add 'Playlist_str' to hover data
             color='Followers',  # Assign color based on 'Followers' values
             color_continuous_scale=color_scale  # Use custom color scale
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
    xaxis_tickangle=-30,
    # plot_bgcolor='rgba(0,0,0)',
    # paper_bgcolor='rgb(0,0,0)',  # black paper background for the entire figure
    margin=dict(t=100),
    title=dict(
        text='Top 5 Highest Reach',
        y=0.9,  # Adjust the title's position on the y-axis
        x=0.5,  # Center the title on the x-axis
        xanchor='center',  # Use the center of the title for x positioning
        yanchor='top'  # Anchor the title to the top of the layout
),
    coloraxis_showscale=False  # Optionally hide color scale legend
    
    )
# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

########################
# SEARCH ADDS BY SONG
########################
st.subheader('Search Adds By Song:')

# Combine Artist & Title for the first dropdown box: 
# Use latest_friday_df from earlier in the code

latest_friday_df['Artist_Title'] = latest_friday_df['Artist'] + " - " + latest_friday_df['Title']
choices = latest_friday_df['Artist_Title'].unique()

# Sort the choices in alphabetical order before displaying in the dropdown
sorted_choices = sorted(choices, key=lambda x: x.lower())

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select New Release:', sorted_choices)

# Filter DataFrame based on selection, then drop unnecessary columns for display
filtered_df = latest_friday_df[latest_friday_df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Order the filtered_df by 'Followers' in descending order
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Format the 'Followers' column to include commas for thousands
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=True, hide_index=True)


###########################
# SEARCH ADDS BY PLAYLIST
###########################
st.write("")
st.subheader('Search Adds By Playlist:')

# Use latest_friday_df from earlier in the code
playlist_choices = sorted(latest_friday_df['Playlist'].unique(), key=lambda x: x.lower())

selected_playlist = st.selectbox('Select Playlist:', playlist_choices, key='playlist_select')

# Filter DataFrame based on the selected playlist
filtered_playlist_df = latest_friday_df[latest_friday_df['Playlist'] == selected_playlist]

# Display all songs in the selected playlist
st.dataframe(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True), hide_index=True, use_container_width=True)

#################################################
# Cover Artists DataFrame 
#################################################

# Filter out rows where either 'Cover_Artist' or 'Image_URL' is None before grouping
# Use latest_friday_df from earlier in the code
filtered_df = latest_friday_df.dropna(subset=['Cover_Artist', 'Image_URL'])

new_cover_artist_df = filtered_df.groupby('Playlist').agg({
    'Image_URL': 'first',
    'Cover_Artist': 'first'
}).reset_index()

final_cover_artist_df = new_cover_artist_df[['Playlist', 'Cover_Artist']]

st.subheader('Cover Artists:')
st.dataframe(final_cover_artist_df, use_container_width=True, hide_index=True)

st.write("") # padding 
st.write("*Note: Cover artist may update before cover images*")

# Playlist packshots
col1, col2, col3 = st.columns(3)

# Create a list of columns for easier access
cols = [col1, col2, col3]

# Total number of playlists
total_playlists = len(new_cover_artist_df)

# Iterate over DataFrame rows
for index, row in new_cover_artist_df.iterrows():
    playlist_name = row['Playlist']
    artist_name = row['Cover_Artist']
    image_url = row['Image_URL']
    
    # Check if this is the last image and if the total number is not divisible by 3, put it in col2
    if index == total_playlists - 1 and total_playlists % 3 != 0:
        col_index = 1  # Explicitly set to use col2
    else:
        # Calculate the column index in a round-robin fashion for all other cases
        col_index = index % 3
    
    # Display the image in the appropriate column with the artist name as the caption
    cols[col_index].image(image_url, caption=f"Cover Artist: {artist_name}", width=200)

st.write('- - - - - -') 

##########################################################

# Calculate the number of adds per playlist and sort for plotting
# Use latest_friday_df from earlier in the code
adds_per_playlist = latest_friday_df['Playlist'].value_counts().sort_values(ascending=True)

# Setting the style for the plot
fig, ax = plt.subplots(figsize=(6, 8), facecolor= '#0E1117')  # Adjust figure size for readability
adds_per_playlist.plot(kind='barh', ax=ax, color='#ab47bc')  # Adjusted to a lighter purple

ax.set_facecolor('#0E1117')
fig.patch.set_facecolor('#0E1117')

# Customise tick parameters for better legibility
ax.tick_params(axis='x', colors='white', labelsize=12)  # Adjust x-axis ticks
ax.tick_params(axis='y', colors='white', labelsize=12)  # Adjust y-axis ticks
ax.set_title('Adds By Playlist', pad=70, weight='bold', color='white', fontsize=20, loc='left')

# Explicitly remove the grid
ax.grid(False)

# Move the x-axis label to the top
ax.xaxis.set_label_position('top')

ax.xaxis.tick_top()

# Set the x-axis label with custom formatting
ax.set_xlabel('No. of New Releases Added', labelpad=20, weight='light', color='white', fontsize=10, loc='left')
ax.set_xticks([10, 20, 30, 40, 50, 60, 70, 80])
ax.tick_params(top=False, left=False, right=False)
# Assume the rest of the code is written
ax.axvline(x=10, ymin=0.01, c='grey', alpha=0.4)

# Remove spines
for location in ['left', 'right', 'top', 'bottom']:
    ax.spines[location].set_visible(False)

st.pyplot(fig)

