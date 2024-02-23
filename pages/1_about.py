import streamlit as st
from functions import save_user_input, is_valid_spotify_link
import re

col1, col2, col3 = st.columns(3)

def show_info():
    """
    Displays information about the app in a Streamlit page.
    """

    # App Title
    st.title('New Music Spotify Playlist Tracker (AU)')
    st.write("""
    This site aims to streamline Friday morning playlist checking for those interested in New Release coverage. 
    
    Not every new release is tracked... the list of new releases focuses on songs that were added to New Music Friday AU & NZ. It then uses this group of songs to check if they were also added to other key AU editorial Spotify playlists and also what positions they recieved.  
    
    """)
    st.write('- - - - - -') 
    # Features
    st.header('Features')
    st.write("""
    - Search adds by song. 
    - Search adds by playlist.
    - See which artists are featured on playlist covers.
    - Artist(s) with the most playlist adds
    - Artist(s) with the highest average playlist position
    - Artist(s) with the highest reach (total playlist likes across each playlist the artist was added to) 
    - Distribution of adds per playlist
    - Playlist cover images and cover artists 
    """)
# Call the function to display the info page content
show_info()

st.write('- - - - - -') 
# List of playlists tracked
st.header('Playlists Tracked')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
- New Music Friday AU & NZ
- Top 50 Australia
- Hot Hits Australia
- Front Left
- A1
- Dance Generation
- Get Popped!
- R&B Connect
- The Flavour
    """)

with col2:
    st.markdown("""


- Fresh Country
- New Dance Beats
- Pop n' Fresh
- Beats n' Bars
- Indie Arrivals
- Rock Out.
- Mellow Styles
- The Drip
- Alt Here

    """)

with col3:
    st.markdown("""

- Breaking Hits
- Chilled Hits
- the hybrid
- Coffee + Chill
- Gentle Acoustic
- triple j's New Music Hitlist
    """)

st.write("")
st.write("")


# Display the input field and submit button
st.write("If you'd like another playlist considered for tracking, submit it's playlist ID below:")
st.write("Please only submit AU Spotify Editorial Playlists, not algorithmic playlists.")

st.markdown("""
### How to Submit a Spotify Playlist ID:

1. In Spotify, navigate to the playlist you'd like to submit.
2. Click the three dots (near the play and shuffle buttons) to open the options menu.
3. Click **'Share'** from the dropdown menu.
4. Select **'Copy link to playlist'** to copy the playlist URL to your clipboard.
5. Paste the copied link into the submission box below.
""")



playlist_link = st.text_input("Paste the Spotify playlist link here:")
submit_button = st.button("Submit")

if submit_button:
    if playlist_link and is_valid_spotify_link(playlist_link):
        # Extracting the playlist ID from the link
        playlist_id = re.search(r'playlist/([a-zA-Z0-9]{22})', playlist_link).group(1)
        
        # Save the extracted playlist ID
        save_user_input(playlist_id)
        
        st.success("Thank you for your submission 😎")
    else:
        st.error("Please submit a valid Spotify playlist link.")



st.write('- - - - - -') 

  # Any Additional Information
st.subheader('Additional Information')
st.write("""
Developer's source code here: 
    """)

st.link_button(label='Github', url='github.com/amcl11')