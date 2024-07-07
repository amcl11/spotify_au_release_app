import streamlit as st
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

st.subheader('Release Comparison (By Artist):')
st.write('Data available from 23rd Feb 2024 onwards')
st.markdown(
    '<p style="font-size: 14px;">This site only tracks releases that were added to NMF AU & NZ</p>', 
    unsafe_allow_html=True
)
st.write("Note: New playlists have been added on 7th June 2024. If a track was added to any of the newly tracked playlists prior to 7th June it won't show up in the comparison.")
st.write('--------------')

def fetch_all_for_selectbox():
    query = text("""
    SELECT "Date", "Artist", "Title", "Playlist", "Position", "Followers"
    FROM nmf_spotify_coverage 
    """)
    with engine.connect() as connection:
        result = connection.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

df = fetch_all_for_selectbox()

# Add this function definition before it's used
def add_ordinal(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"

def correct_artist_name(name):
    if name is None:
        return name
    special_cases = {
        'charli xcx': 'Charli xcx',
        # Add more special cases here
    }
    
    lowercase_name = name.lower()
    if lowercase_name in special_cases:
        return special_cases[lowercase_name]
    else:
        return name  # Return the original name without modification

# Split the 'Artist' column by ", " and then explode the DataFrame to normalize it
df_normalized = df.assign(Artist=df['Artist'].str.split(', ')).explode('Artist')

# Apply the correct stylization to artist names
df_normalized['Artist_Corrected'] = df_normalized['Artist'].apply(correct_artist_name)

# Group by the corrected artist name and count distinct titles 
artist_title_counts = df_normalized.groupby('Artist_Corrected')['Title'].nunique()

# Filter artists with more than one distinct title
filtered_artists = artist_title_counts[artist_title_counts > 1]

# Get the correct stylization for each artist
select_box_options = df_normalized[df_normalized['Artist_Corrected'].isin(filtered_artists.index)]['Artist_Corrected'].unique()

# Sort the list of artists alphabetically, ignoring case
select_box_options_sorted = sorted(select_box_options, key=lambda x: x.lower())

# Populate a selectbox with the sorted artist names
selected_artist = st.selectbox('Select Artist:', select_box_options_sorted)

# Fetch and display data for the selected artist
if selected_artist:
    # Filtering the normalized dataframe for the selected artist (case-insensitive)
    artist_data = df_normalized[df_normalized['Artist_Corrected'] == selected_artist]

    # Convert 'Date' from string to datetime format
    artist_data['Date'] = pd.to_datetime(artist_data['Date'])

    # Format 'Date' as "22nd March, 2024"
    artist_data['Formatted_Date'] = artist_data['Date'].dt.day.apply(add_ordinal) + " " + artist_data['Date'].dt.strftime('%B, %Y')

    # Get the total followers for each title
    total_followers_per_title = artist_data.groupby('Title')['Followers'].sum().reset_index()
    
    # Sort the titles by total followers in descending order
    sorted_titles = total_followers_per_title.sort_values(by='Followers', ascending=False)['Title']

    titles_of_interest = artist_data['Title'].unique()

    # Use this order for the x-axis order in the plot
    artist_data_filtered = artist_data[artist_data['Title'].isin(titles_of_interest)]

    # Convert all titles to strings
    artist_data_filtered['Title'] = artist_data_filtered['Title'].astype(str)

    # Stacked bar chart for Reach comparison
    fig = px.bar(artist_data_filtered, 
        x='Title', 
        y='Followers', 
        color='Playlist', 
        text='Playlist', 
        custom_data=['Position', 'Formatted_Date'],
        category_orders={'Title': sorted_titles.astype(str).tolist()})
    
    # Update the layout for a better visual representation
    fig.update_layout(
        barmode='stack',
        title={
            'text': "Total Reach on Release (Fri-Wed)",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="",
        yaxis_title="",
        legend_title="Playlists",
        height=400,
        yaxis=dict(
            tick0=0,
            dtick=500000
        )
    )

    fig.update_xaxes(tickangle=-25, type='category')  # Set x-axis type to 'category'

    # Customize hover data
    fig.update_traces(
        textposition='inside',
        hovertemplate="<b>Release Date:</b> %{customdata[1]}<br>" +
                      "<b>Playlist:</b> %{text}<br>" +
                      "<b>Playlist Reach:</b> %{y:,.0f}<br>" +
                      "<b>Position:</b> %{customdata[0]}<extra></extra>"
    )

    st.write(
        """
        <style>
            .my-text {
                font-size: 11px;
                font-family: monospace;
            }
        </style>
        <p class="my-text">Hover over chart for additional info:</p>
        """,
        unsafe_allow_html=True,
    )
    # Show the figure in Streamlit
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})