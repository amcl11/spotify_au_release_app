import streamlit as st
import streamlit.components.v1 as components

# Read the HTML file
with open("components/google_analytics.html", "r") as f:
    google_analytics = f.read()

# Load the Google Analytics script in your Streamlit app
components.html(google_analytics, height=0, width=0, scrolling=False)

def contact_page():
    st.subheader("Questions or feedback?")
    st.markdown("Email: [new.music.playlist.tracker@gmail.com](mailto:new.music.playlist.tracker@gmail.com)")

contact_page()