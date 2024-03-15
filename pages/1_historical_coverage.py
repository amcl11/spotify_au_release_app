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

# Format artist names
if len(most_reach_title_df) > 1:
    artist_names_reach = ", ".join(most_reach_title_df['Artist'].tolist()[:-1]) + " and " + most_reach_title_df['Artist'].tolist()[-1]
else:
    artist_names_reach = most_reach_title_df['Artist'].iloc[0]

# Display result
with col2:
    label = ":grey[Highest Reach]"
    st.metric(label=label, value=f"{artist_names_reach}", delta=f"{max_followers:,}", help='Total reach across AU playlist adds. Only based on the tracked playlists.', delta_color='normal')


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

# Format the artist names

if len(most_added_artists_df) > 1:
    artist_names = " & ".join(most_added_artists_df['Artist'].tolist()[:-1]) + " and " + most_added_artists_df['Artist'].tolist()[-1]
else:
    artist_names = most_added_artists_df['Artist'].iloc[0]

# Display the result
with col2:
    label = ":grey[Most Added]"
    st.metric(label=label, value=f"{artist_names}", delta=f"Added to {max_adds} playlists")

####################################
# HIGHEST AVERAGE PLAYLIST POSITION 
####################################

# Calculate the average position by grouping by 'Title' and 'Artist'
avg_position = df.groupby(['Title', 'Artist'])['Position'].mean()

# Find the index (Title, Artist) of the minimum average position
best_avg_playlist_position_by_artist = avg_position.idxmin()

# Extract just the 'Artist' from the index
best_artist = best_avg_playlist_position_by_artist[1]  # Access the second element for 'Artist'

# Find the minimum average position
best_avg = avg_position.min()

with col2:
    label = ":grey[Highest Average Playlist Position]"
    st.metric(label=label, value=f"{best_artist}", delta=f"{best_avg:.0f}", delta_color='normal', help='Averages all positions across any new AU playlist additions')
    
########################################################## 
# TOP 5 HIGHEST REACH CHART
########################################################## 

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
#         y=1,  # Adjust the title's position on the y-axis
#         x=0.6,  # Center the title on the x-axis
#         xanchor='center',  # Use the center of the title for x positioning
#         yanchor='top'  # Anchor the title to the top of the layout
        
# ),
#     coloraxis_showscale=False  # Optionally hide color scale legend
    
#     )

# Updated "Top 5 Highest Reach" title to ensure positioning doesn't change 

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

#PREVIOUS CODE#
# st.subheader('Search Adds By Song:')

# # Combine Artist & Title for the first dropdown box: 
# df['Artist_Title'] = df['Artist'] + " - " + df['Title']
# choices = df['Artist_Title'].unique()

# # Sort the choices in alphabetical order before displaying in the dropdown
# sorted_choices = sorted(choices, key=lambda x: x.lower())

# # Dropdown for user to select an artist and title
# selected_artist_title = st.selectbox('Select New Release:', sorted_choices)

# # Filter DataFrame based on selection, then drop unnecessary columns for display
# filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# # Order the filtered_df by 'Followers' in descending order
# ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# # Format the 'Followers' column to include commas for thousands
# ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}")

# # Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
# st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=False, hide_index=True)

# st.write('- - - - - -') 


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
selected_artist_title = st.selectbox('Select New Release:', sorted_choices)

# Add 'Artist_Title' to the original dataframe for filtering based on the dropdown selection
df['Artist_Title'] = df.apply(lambda row: f"{row['Artist']} - {row['Title']}" if pd.notnull(row['Artist']) and pd.notnull(row['Title']) else None, axis=1)

# Now filter the original DataFrame based on selection, this time it includes 'Artist_Title'
filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Continue with sorting and displaying the data as before
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}" if pd.notnull(x) else "N/A")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=False, hide_index=True)



###########################
# SEARCH ADDS BY PLAYLIST
###########################
# st.subheader('Search Adds By Playlist:')

# playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())

# selected_playlist = st.selectbox('Select Playlist:', playlist_choices, key='playlist_select')

# # Filter DataFrame based on the selected playlist
# filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# #testing this for mobile no horizontal scroll
# st.data_editor(
#     data=filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True),
#     disabled=True,  # Ensures data cannot be edited
#     use_container_width=False,  # Adjust based on your layout needs
#     column_config={
#         "Artist": {"width": 150},  # Set tighter width
#         "Title": {"width": 120},   # Set width 
#         "Position": {"width": 58}
#     },
#     hide_index=True
# )

st.write("")
st.subheader('Search Adds By Playlist:')

# Use latest_friday_df from earlier in the code
playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())

selected_playlist = st.selectbox('Select Playlist:', playlist_choices, key='playlist_select')

# Filter DataFrame based on the selected playlist
filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# Check if 'Artist' and 'Title' columns only contain None values
if filtered_playlist_df[['Artist', 'Title']].isnull().all(axis=None):
    st.markdown(f"<span style='color: #FAFAFA;'>No New Releases added to <span style='color: salmon;'>**{selected_playlist}**</span>", unsafe_allow_html=True)



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
# st.dataframe(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True), hide_index=True, use_container_width=True)




    


