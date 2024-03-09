import streamlit as st

def set_theme():
    st.markdown(
        """
        <style>
        /* Main background */
        .stApp {
            background-color: #000000;
        }

        /* Text color for headings and button in the main app */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        .stButton button {
            color: #FAFAFA;
        }

        /* Sidebar background */
        .stSidebar > div:first-child, .stSidebar .css-1aumxhk {
            background-color: #055483 !important;
            color: #FAFAFA !important;
        }

        /* Sidebar selectbox, adjust class name according to the latest Streamlit version */
        .stSelectbox > div, .css-2b097c-container {
            background-color: #055483 !important;
            color: #FAFAFA !important;
        }

        /* Adjust selectbox dropdown color */
        .css-26l3qy-menu {
            background-color: #055483 !important;
            color: #FAFAFA !important;
        }

        /* Button styles in sidebar */
        .stSidebar .stButton button {
            background-color: #055483 !important;
            color: #FAFAFA !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_theme()
