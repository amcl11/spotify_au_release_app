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

# Set right aligned note about Desktop viewing 
col1, col2, col3 = st.columns([6, 6, 6])

with col3:
    st.write(
        """
        <style>
            .my-text {
                font-size: 10px;
                font-family: monospace;
            }
        </style>
        <p class="my-text">[Best viewed on Desktop]</p>
        """,
        unsafe_allow_html=True,
    )
    
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
st.markdown("""
    <style>
    .small-font {
        font-size: 14px;
    }
    </style>
    
    <p class="small-font">Note: This means New Releases that did not get added to NMF AU & NZ will not show up on this site - focusing on the releases that Spotify has chosen to feature in NMF.</p>
    """, unsafe_allow_html=True)

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
        st.metric(
    label=":gray[Highest Reach]",
    value=f"{artist} - '{title}'",
    delta="{:,}".format(int(reach)),  # Format 'reach' with commas and no decimal places
    help='Total reach across AU playlist adds. Only based on the tracked playlists.'
)

#######################
# MOST ADDED METRIC
#######################

# Use latest_friday_df from earlier in the code
# Find the titles with the most entries
most_added = latest_friday_df.groupby(['Title', 'Artist']).size().reset_index(name='Count')
max_count = most_added['Count'].max()
most_added_max = most_added[most_added['Count'] == max_count].reset_index(drop=True)

# Use a variable to track if the label has been displayed
label_displayed = False

for i, (index, row) in enumerate(most_added_max.iterrows()):
    title, artist = row['Title'], row['Artist']
    # For the first item, display the label
    if i == 0:
        label = ":grey[Most Added]"
    else:
        # For subsequent items, check if the title is different.
        # If it is, update the label to be displayed; if not, keep the label empty
        label = "" if title == most_added_max.iloc[i-1]['Title'] else":grey[Most Added]"

    with col1:
        st.metric(label=label, value=f"{artist} - '{title}'", delta=f"Added to {max_count} playlists")
        

####################################
# HIGHEST AVERAGE PLAYLIST POSITION 
####################################

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
        st.metric(label=":gray[Highest Average Playlist Position]", value=f"{artist} - '{title}'", delta=f"Average Playlist Position: {round(min_avg_position)}", help='Averages all positions across any new AU playlist additions')

st.write("----")
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

# fig.update_layout(
#     xaxis_title="",
#     yaxis_title="Total  Reach",
#     yaxis=dict(type='linear'),
#     xaxis_tickangle=-30,
#     # plot_bgcolor='rgba(0,0,0)',
#     # paper_bgcolor='rgb(0,0,0)',  # black paper background for the entire figure
#     margin=dict(t=10),
#     title=dict(
#         text='Top 5 Highest Reach',
#         font=dict(
#             family="Aria, sans-serif",
#             size=14,
#             color="#FAFAFA"
#         ),
#         y=0.95,  # Adjust the title's position on the y-axis
#         x=0.65,  # Center the title on the x-axis
#         xanchor='center',  # Use the center of the title for x positioning
#         yanchor='top'  # Anchor the title to the top of the layout
        
# ),
#     coloraxis_showscale=False  # Optionally hide color scale legend
    
#     )

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
filtered_df_for_artist_title = latest_friday_df.dropna(subset=['Artist', 'Title'])

# Temporarily create 'Artist_Title' in the filtered dataframe for dropdown options
filtered_df_for_artist_title['Artist_Title'] = filtered_df_for_artist_title['Artist'] + " - " + filtered_df_for_artist_title['Title']

# Ensure unique values and sort them for the dropdown
choices = filtered_df_for_artist_title['Artist_Title'].unique()
sorted_choices = sorted(choices, key=lambda x: x.lower())

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select New Release:', sorted_choices)

# Add 'Artist_Title' to the original dataframe for filtering based on the dropdown selection
latest_friday_df['Artist_Title'] = latest_friday_df.apply(lambda row: f"{row['Artist']} - {row['Title']}" if pd.notnull(row['Artist']) and pd.notnull(row['Title']) else None, axis=1)

# Now filter the original DataFrame based on selection, this time it includes 'Artist_Title'
filtered_df = latest_friday_df[latest_friday_df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Continue with sorting and displaying the data as before
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Before displaying, round 'Followers' to no decimal places and format
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{round(x):,}" if pd.notnull(x) else "N/A")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=False, hide_index=True)

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

# # Display all songs in the selected playlist
# st.dataframe(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True), hide_index=True, use_container_width=False)

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
st.dataframe(final_cover_artist_df, use_container_width=False, hide_index=True)

st.write("") # padding 
st.write("*Cover artist may update before cover images*")

#############################
# Playlist packshots
#############################

# col1, col2 = st.columns(2)  # Use two columns instead of three

# # Update the list of columns for easier access
# cols = [col1, col2]

# # Total number of playlists remains the same
# total_playlists = len(new_cover_artist_df)

# # Iterate over DataFrame rows 
# for index, row in new_cover_artist_df.iterrows():
#     playlist_name = row['Playlist']
#     artist_name = row['Cover_Artist']
#     image_url = row['Image_URL']
    
#     # For two columns, adjust the logic accordingly
#     if index == total_playlists - 1 and total_playlists % 2 != 0:
#         col_index = 1  # Use col2 for the last image if odd number of playlists
#     else:
#         col_index = index % 2  # Use modulo 2 for two columns
    
#     # Display the image in the selected column with the artist name as the caption
#     cols[col_index].image(image_url, caption=f"Cover Artist: {artist_name}", width=300)

#################################################################################
# New Playlist packshots code - to centre the final image if the number is odd. 
#################################################################################

# Determine if there is an odd number of playlists
total_playlists = len(new_cover_artist_df)
is_odd = total_playlists % 2 != 0

# If the number of playlists is odd, then we reserve the last spot for the single centered image
if is_odd:
    last_image_col_index = total_playlists - 1  # Index of the last image
else:
    last_image_col_index = None  # No special handling needed if even

# Create two columns for the images
col1, col2 = st.columns(2)

# Initialize an index for the last column, will be used if there's an odd number of images
last_col = None

# Iterate over DataFrame rows
for index, row in new_cover_artist_df.iterrows():
    playlist_name = row['Playlist']
    artist_name = row['Cover_Artist']
    image_url = row['Image_URL']
    
    # Check if we're at the last image and if it should be centered
    if index == last_image_col_index:
        # Create a new set of columns for the last image
        _, last_col, _ = st.columns([1, 2, 1])  # Middle column is twice as wide to center the image
        last_col.image(image_url, caption=f"Cover Artist: {artist_name}", width=300)
    else:
        # Use the two columns as before
        col_index = index % 2
        col = col1 if col_index == 0 else col2
        col.image(image_url, caption=f"Cover Artist: {artist_name}", width=300)

st.write('- - - - - -') 


################################
# UPDATED ADDS BY PLAYLIST GRAPH
################################

# # Calculate the number of adds per playlist and sort for plotting
# # Use latest_friday_df from earlier in the code

# Filter out rows with both null 'Artist' and 'Title'
non_null_adds_df = latest_friday_df.dropna(subset=['Artist', 'Title'])

# Count the number of adds per playlist only for non-null 'Artist' and 'Title'
adds_per_playlist = non_null_adds_df['Playlist'].value_counts().reindex(latest_friday_df['Playlist'].unique(), fill_value=0).sort_values()

fig, ax = plt.subplots(figsize=(6, 8), facecolor= '#0E1117')
adds_per_playlist.plot(kind='barh', ax=ax, color='#ab47bc')

ax.set_facecolor('#0E1117')
fig.patch.set_facecolor('#0E1117')

# Customise tick parameters 
ax.tick_params(axis='x', colors='white', labelsize=12, bottom=False, labelbottom=False)  # Hide x ticks
ax.tick_params(axis='y', colors='white', labelsize=12)
ax.tick_params(axis='y', which='both', left=False, labelleft=True)  # Remove Y-axis ticks but keep labels

# Reduced padding between title and x-axis label
ax.set_title('Adds By Playlist', pad=15, weight='bold', color='white', fontsize=20, loc='left')

ax.grid(False)
ax.xaxis.set_label_position('top')

# Custom formatting for x-axis label with reduced label padding
ax.set_xlabel('No. of New Releases Added', labelpad=10, weight='light', color='white', fontsize=10, loc='left')

# Add text labels at the end of each bar
for index, value in enumerate(adds_per_playlist):
    ax.text(value + 1, index, str(value), color='white', va='center', ha='left')

# Remove spines
for location in ['left', 'right', 'top', 'bottom']:
    ax.spines[location].set_visible(False)

st.pyplot(fig)




