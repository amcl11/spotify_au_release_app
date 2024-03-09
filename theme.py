import streamlit as st

def set_theme():
  
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #000000;
            color: #FAFAFA;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #FAFAFA;
        }
        .stButton button {
            background-color: #055483;
            color: #FAFAFA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )