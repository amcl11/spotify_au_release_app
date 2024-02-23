import streamlit as st

col1, col2, col3 = st.columns(3)

def show_info():
    """
    Displays information about the app in a Streamlit page.
    """

    # App Title
    st.title('New Music Spotify Playlist Tracker (AU)')
    st.write("""
    This site aims to streamline Friday morning playlist checking for those interested in New Release coverage. 
    
    Not every single new release is tracked... the list of new releases focuses on songs that were added to New Music Friday AU & NZ. It then uses this group of songs to check if they were also added to other key AU editorial Spotify playlists and also what positions they recieved.  
    
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
    - Artist(s) with the highest reach (total playlist likes across all adds) 
    - Distribution of adds per playlist
    - Playlist cover images 
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


st.write('- - - - - -') 

  # Any Additional Information
st.subheader('Additional Information')
st.write("""
Source code here: 
    """)

st.link_button(label='Github', url='github.com/amcl11')