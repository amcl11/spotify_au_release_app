# import streamlit as st

# def set_theme():
  
#     st.markdown(
#         """
#         <style>
#         .stApp {
#             background-color: #000000;
#             color: #FAFAFA;
#         }
#         .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
#             color: #FAFAFA;
#         }
#         .stButton button {
#             background-color: #055483;
#             color: #FAFAFA;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )



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
        .stSidebar > div:first-child {
            background-color: #055483;
            color: #055483;
        }

        /* Sidebar headings */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3, .stSidebar .stMarkdown h4, 
        .stSidebar .stMarkdown h5, .stSidebar .stMarkdown h6 {
            color: #FAFAFA;
        }

        /* Sidebar widgets */
        .stSidebar .stSelectbox .css-2b097c-container {
            background-color: #055483;
            color: #055483;
        }

        /* Adjust selectbox dropdown color */
        .stSelectbox .css-1okebmr-indicatorSeparator, .stSelectbox .css-1hwfws3 {
            background-color: #055483;
        }

        /* Adjust selectbox text and arrow color */
        .stSelectbox .css-1uccc91-singleValue, .stSelectbox .css-1gtu0rj-indicatorContainer {
            color: #055483;
        }

        /* Button styles in sidebar */
        .stSidebar .stButton button {
            background-color: #055483;
            color: #055483;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_theme()
