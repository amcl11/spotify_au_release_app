import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import plotly.express as px

# Define a function to load the CSV data and decorate it with st.cache_data
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

# Load cover image and cover artist data from saved dictionaries as JSON
with open('cover_art_data.json') as f:
    data = json.load(f)

cover_art_dict = data['filtered_cover_art_dict']
cover_artist_dict = data['cover_artist_dict']

# Use the load_data function to load your preprocessed data
df = load_data('streamlit.csv')

left_column, middle_column, right_column = st.columns(3)
left_column.image('images/nmf_logo.png')

todays_date = datetime.now().strftime("%A, %d %B, %Y")  # Format the date as Weekday, Day, Month, Year
right_column.write(todays_date)


st.title('New Release Playlist Adds:')
st.write('---')  # Add a visual separator
st.write('This site pulls all songs added to *New Music Friday AU & NZ*, and then checks to see if these songs have also been added to any key Australian editorial playlists.')  
st.write('For more info and the list of playlists that are tracked, check the About page.')  
st.write('---')  # Add a visual separator


col1, col2, col3 = st.columns([300, 0.5, 0.5])  

st.markdown(
    """
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

##########################################################
##########################################################

# Most Added Artists
# Count the occurrences of each artist
artist_counts = df['Artist'].value_counts()
max_adds = artist_counts.max()
most_added_artists = artist_counts[artist_counts == max_adds].index.tolist()
artist_names = " & ".join(most_added_artists[:-1]) + " and " + most_added_artists[-1] if len(most_added_artists) > 1 else most_added_artists[0]
with col1:
    st.metric(label="Most Added", value=f"{artist_names}", delta=f"Added to {max_adds} playlists")
    st.write("")
# Highest Follower Count
# Sum the followers count for each artist
artist_followers = df.groupby('Artist')['Followers'].sum()

# Find the maximum followers count
max_followers = artist_followers.max()

# Find all artists with the highest followers count
most_reach_artists = artist_followers[artist_followers == max_followers].index.tolist()

# Format the artist names for display
artist_names_reach = ", ".join(most_reach_artists[:-1]) + " and " + most_reach_artists[-1] if len(most_reach_artists) > 1 else most_reach_artists[0]

with col1:
    st.metric(label="Highest Reach", value=f"{artist_names_reach}", delta=f"{max_followers:,}", help='Total reach across playlist adds. Only based on the tracked playlists.', delta_color='normal')
    st.write("")
# Artist with the highest average playlist positioning 
avg_position = df.groupby('Artist')['Position'].mean()
best_avg_playlist_position_by_artist = avg_position.idxmin()
best_avg = avg_position.min()

with col1:
    st.metric(label="Highest Average Playlist Position", value=f"{best_avg_playlist_position_by_artist}", delta=f"{best_avg:.0f}", delta_color='normal', help='Averages all positions across any new playlist additions')


##########################################################
##########################################################



top_artists_reach = df.groupby('Artist').agg({
    'Followers': 'sum',
    'Playlist': lambda x: list(x.unique())  # Creates a list of unique playlists for each artist
})

# Sort the DataFrame based on 'Followers' while maintaining the whole DataFrame
sorted_top_artists_reach = top_artists_reach.sort_values(by='Followers', ascending=False)

# Select the top 5 artists while keeping all columns ('Followers' and 'Playlist')
results_with_playlist = sorted_top_artists_reach.head(5)

# Convert 'Playlist' list to a string for each artist
results_with_playlist['Playlist_str'] = results_with_playlist['Playlist'].apply(lambda x: ', '.join(x))

# Ensure 'Artist' is a column for Plotly (if 'Artist' was the index)
results_with_playlist = results_with_playlist.reset_index()

# Create a color scale
# This creates a gradient from light to dark blue
# color_scale = [[0, 'salmon'], [0.5, 'red'], [1, 'darkred']]
# color_scale = [[0, 'lavender'], [0.5, 'mediumorchid'], [1, 'darkmagenta']]
# color_scale = [[0, 'orange'], [0.5, 'orangered'], [1, 'darkred']]
color_scale = [[0, 'lightsalmon'], [0.5, 'coral'], [1, 'orangered']]

# Create a bar chart using Plotly Express
fig = px.bar(results_with_playlist, x='Artist', y='Followers',
             text='Followers',
             hover_data=['Playlist_str'],  # Add 'Playlist_str' to hover data
             color='Followers',  # Assign color based on 'Followers' values
             color_continuous_scale=color_scale  # Use the custom color scale
             )

# Custom hover template to include Playlist information
fig.update_traces(hovertemplate='<b>%{x}</b><br>Reach: %{y:,}<br>Playlists: %{customdata[0]}')

# Display the exact number of followers on top of each bar and adjust other aesthetics
fig.update_traces(texttemplate='%{text:.3s}', textposition='inside')
fig.update_layout(
    xaxis_title="",
    yaxis_title="Total Reach",
    yaxis=dict(type='linear'),
    xaxis_tickangle=-30,
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=100),
    title=dict(
        text='Top 5 Highest Reach',
        y=0.9,  # Adjust the title's position on the y-axis
        x=0.5,  # Center the title on the x-axis
        xanchor='center',  # Use the center of the title for x positioning
        yanchor='top'  # Anchor the title to the top of the layout
),
    coloraxis_showscale=False  # Optionally hide the color scale legend
    
    )
# Display the figure in Streamlit
st.plotly_chart(fig, use_container_width=True)

##########################################################

# Combine Artist & Title for the first dropdown box: 
df['Artist_Title'] = df['Artist'] + " - " + df['Title']
choices = df['Artist_Title'].unique()

# Sort the choices in alphabetical order before displaying in the dropdown
sorted_choices = sorted(choices, key=lambda x: x.lower())

st.subheader('Search Adds By Song:')

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select a New Release:', sorted_choices)

# Filter DataFrame based on selection, then drop unnecessary columns for display
filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Order the filtered_df by 'Followers' in descending order
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Format the 'Followers' column to include commas for thousands
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}")

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.dataframe(ordered_filtered_df[['Playlist', 'Position', 'Followers']], use_container_width=True, hide_index=True)

# New Section for Playlist selection
# Add space
st.write("")
# Add space
st.write("")
st.subheader('Search Adds By Playlist:')

playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())

selected_playlist = st.selectbox('Select a Playlist:', playlist_choices, key='playlist_select')
# Filter DataFrame based on the selected playlist
filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# Display all songs in the selected playlist
st.dataframe(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True), hide_index=True, use_container_width=True)

# Cover Artists 
# Display the dictionary in the app
st.subheader('Cover Artists:')
cover_artist_df = pd.DataFrame(list(cover_artist_dict.items()), columns=['Playlist', 'Cover Artist'])
st.dataframe(cover_artist_df, use_container_width=True, hide_index=True)



st.write('- - - - - -') 

##########################################################


st.write("*Note: Cover artist may update before cover images*")


# # Playlist packshots
col1, col2, col3 = st.columns(3)

# Create a list of columns for easier access
cols = [col1, col2, col3]

# Total number of playlists
total_playlists = len(cover_art_dict)

# Iterate over your dictionary items
for index, (playlist_name, image_url) in enumerate(cover_art_dict.items()):
    # Get the artist name using the playlist name from the cover_artist_name_dict
    artist_name = cover_artist_dict.get(playlist_name, "Artist Unknown")
    
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
adds_per_playlist = df['Playlist'].value_counts().sort_values(ascending=True)

# Setting the style for the plot
plt.style.use('dark_background')  # Use a dark background style

# Plotting
fig, ax = plt.subplots(figsize=(6, 8))  # Adjust figure size for readability
adds_per_playlist.plot(kind='barh', ax=ax, color='#ab47bc')  # Adjusted to a lighter purple

# Customize tick parameters for better legibility
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


