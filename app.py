import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define a function to load the data and decorate it with st.cache_data
@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

# Use the load_data function to load your preprocessed data
df = load_data('streamlit.csv')

# Streamlit app UI
st.title('New Release AU - Spotify Playlist Adds:')

st.write('---')  # Add a visual separator

st.write('Note: This site tracks limited playlists, and is specifically for the AU market.')  # Add a visual separator
st.write('It pulls all tracks that were added to New Music Friday AU & NZ and then checks to see which other prominent playlists (majority AU) those new releases also were added to.') 

st.write('---')  # Add a visual separator

# Combine Artist & Title for the first dropdown box: 
df['Artist_Title'] = df['Artist'] + " - " + df['Title']
choices = df['Artist_Title'].unique()

# Sort the choices in alphabetical order before displaying in the dropdown
sorted_choices = sorted(choices, key=lambda x: x.lower())

# Dropdown for user to select an artist and title
selected_artist_title = st.selectbox('Select a New Release:', sorted_choices)

# Filter DataFrame based on selection, then drop unnecessary columns for display
filtered_df = df[df['Artist_Title'] == selected_artist_title].drop(columns=['Artist', 'Title', 'Artist_Title'])

# Order the filtered_df by 'Followers' in descending order
ordered_filtered_df = filtered_df.sort_values(by='Followers', ascending=False)

# Format the 'Followers' column to include commas for thousands
ordered_filtered_df['Followers'] = ordered_filtered_df['Followers'].apply(lambda x: f"{x:,}")

# #hack to remove index from table 
ordered_filtered_df = ordered_filtered_df.assign(hack='').set_index('hack')

# Display the table with only the 'Playlist', 'Position', and 'Followers' columns, ordered by 'Followers'
st.table(ordered_filtered_df[['Playlist', 'Position', 'Followers']])


# New Section for Playlist selection
st.write('---')  # Add a visual separator
st.subheader('Browse Newly Added Songs by Playlist:')
playlist_choices = sorted(df['Playlist'].unique(), key=lambda x: x.lower())
selected_playlist = st.selectbox('Select a Playlist:', playlist_choices, key='playlist_select')
# Filter DataFrame based on the selected playlist
filtered_playlist_df = df[df['Playlist'] == selected_playlist]

# #hack to remove index from table 
filtered_playlist_df = filtered_playlist_df.assign(hack='').set_index('hack')

# Display all songs in the selected playlist
st.table(filtered_playlist_df[['Artist', 'Title', 'Position']].sort_values(by='Position', ascending=True))

st.write('---')  # Add a visual separator

# Most Added Artists
# Count the occurrences of each artist
artist_counts = df['Artist'].value_counts()

# Find the maximum number of adds
max_adds = artist_counts.max()

# Find all artists with the most adds
most_added_artists = artist_counts[artist_counts == max_adds].index.tolist()

# Format the artist names for display
if len(most_added_artists) > 1:
    artist_names = ", ".join(most_added_artists[:-1]) + " and " + most_added_artists[-1]
    st.write(f"The artists with the most playlist adds are {artist_names} with {max_adds} playlist adds each.")
else:
    st.write(f"The artist with the most playlist adds is {most_added_artists[0]} with {max_adds} playlist adds.")


# Highest Follower Count
# Sum the followers count for each artist
artist_followers = df.groupby('Artist')['Followers'].sum()

# Find the maximum followers count
max_followers = artist_followers.max()

# Find all artists with the highest followers count
most_reach_artists = artist_followers[artist_followers == max_followers].index.tolist()

# Format the artist names for display
if len(most_reach_artists) > 1:
    artist_names = ", ".join(most_reach_artists[:-1]) + " and " + most_reach_artists[-1]
    st.write(f"The artists with the most reach are {artist_names} with a total of {max_followers:,} playlist followers each.")
else:
    st.write(f"The artist with the most reach is {most_reach_artists[0]} with a total of {max_followers:,} playlist followers.")



# Artist with the highest avergae playlist positioning 
avg_position = df.groupby('Artist')['Position'].mean()
best_avg_playlist_position_by_artist = avg_position.idxmin()
best_avg = avg_position.min()
# Display the result
st.write(f"The artist with the best average playlist position is {best_avg_playlist_position_by_artist} with an average position of {best_avg:.1f}")



st.write('---')  # Add a visual separator

# Calculate the number of adds per playlist and sort for plotting
adds_per_playlist = df['Playlist'].value_counts().sort_values(ascending=True)

# Setting the style for the plot
plt.style.use('dark_background')  # Use a dark background style

# Plotting
fig, ax = plt.subplots(figsize=(8, 10))  # Adjust figure size for readability
adds_per_playlist.plot(kind='barh', ax=ax, color='#ab47bc')  # Adjusted to a lighter purple

# Customize tick parameters for better legibility
ax.tick_params(axis='x', colors='white', labelsize=12)  # Adjust x-axis ticks
ax.tick_params(axis='y', colors='white', labelsize=12)  # Adjust y-axis ticks

# Set labels and title with white text and larger font sizes
ax.set_xlabel('New Songs Added', labelpad=10, weight='bold', color='white', fontsize=14, loc='center')
ax.set_title('Distribution of New Song Adds Across Playlists', pad=20, weight='bold', color='white', fontsize=16)

ax.set_xticks([20, 40, 60, 80])
ax.xaxis.tick_top()
ax.tick_params(top=False, left=False)

# Remove spines
for location in ['left', 'right', 'top', 'bottom']:
    ax.spines[location].set_visible(False)

# Display the plot in Streamlit, without needing plt.show()
st.pyplot(fig)
