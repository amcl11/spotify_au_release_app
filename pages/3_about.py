import streamlit as st
from functions import save_user_input, is_valid_spotify_link
import re

col1, col2, col3 = st.columns(3)


# App Title
st.title('New Music Playlist Tracker (AU)')
st.write("""


This site streamlines Friday morning playlist checking for those interested in new release coverage on Spotify in Australia.

Songs that have been added to <span style='color: salmon;'>New Music Friday AU & NZ</span> are fetched and then checked against key editorial playlists.

This means new releases that did not get added to NMF AU & NZ (e.g., additional album tracks, previous releases that have picked up new playlist additions, etc.) will not show up on this site—focusing on the brand new releases that Spotify has chosen to feature in NMF AU/NZ.

*Historical coverage is a snapshot of playlist additions between Friday (release) and Wednesday 9:00 AM AEST.

    
""", unsafe_allow_html=True)

st.write('- - - - - -') 
# # Features
# st.header('Features')
st.write("""
- Artist(s) with the `highest reach` (total playlist likes across each playlist the artist was added to) 
- Artist(s) with the `most playlist adds`
- Artist(s) with the `highest average playlist position`

- Search `adds by song`. 
- Search `adds by playlist`.
- See which artists are featured on `playlist covers`.
- `Release comparison (by artist)` 
- `Top Performers` - Comparing highest reach releases across the available weeks (23rd Feb onwards).
""")
st.write("")
# List of playlists tracked
st.subheader('Playlists Tracked:')
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
- Fresh Country
- New Dance Beats
- Pop n' Fresh
    """)

with col2:
    st.markdown("""



- Beats n' Bars
- Indie Arrivals
- Rock Out.
- Mellow Styles
- The Drip
- Alt Here
- Breaking Hits
- Chilled Hits
- the hybrid
- Coffee + Chill
- Gentle Acoustic


    """)

with col3:
    st.markdown("""


- triple j's New Music Hitlist
- Local Hype
- Local Noise 
- Long Live DnB
- Blak Australia  
- Homegrown + Heavy 
- Big Ancestry Energy
- Proppa Bars
- On One
- Afro Fusion
""")

st.write("")
st.write("")


# # Display the input field and submit button
# st.write("If you'd like another playlist considered for tracking submit it's playlist ID below:")

# st.markdown("""
# #### Submit a Spotify Playlist ID:

# 1. In Spotify, navigate to the playlist you'd like to submit.
# 2. Click the three dots (near the play and shuffle buttons) to open the options menu.
# 3. Click **'Share'** from the dropdown menu.
# 4. Select **'Copy link to playlist'** to copy the playlist URL.
# 5. Paste the copied link into the submission box below.
# """)

# playlist_link = st.text_input("Paste Spotify playlist link here:")
# submit_button = st.button("Submit")

# if submit_button:
#     if playlist_link and is_valid_spotify_link(playlist_link):
        
#         # Extracting the playlist ID from the link
#         playlist_id = re.search(r'playlist/([a-zA-Z0-9]{22})', playlist_link).group(1)
        
#         # Save the extracted playlist ID
#         save_user_input(playlist_id)
        
#         st.success("Submission received.")
#     else:
#         st.error("Please submit a valid Spotify playlist link.")
        

st.write("-----")

# st.subheader("Data Freshness:")

# st.write("The schedule below outlines the current data pull frequency from Spotify's API.")

st.markdown(
    """
    <style>
        .my-text {
            font-size: 14px;
            font-family: monospace;
        }
    </style>
    <div class="my-text">
        Contact: 
        <br>
        <a href="mailto:new.music.playlist.tracker@gmail.com">new.music.playlist.tracker@gmail.com</a>
    </div>
    """,
    unsafe_allow_html=True
)










