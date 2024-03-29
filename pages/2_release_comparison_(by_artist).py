import streamlit as st
import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
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
st.write('--------------')

def fetch_all_for_selectbox():
    query = """
    SELECT "Date", "Artist", "Title", "Playlist", "Position", "Followers"
    FROM nmf_spotify_coverage 
    """
    df = pd.read_sql_query(query, engine)
    return df

df = fetch_all_for_selectbox()

# Split the 'Artist' column by ", " and then explode the DataFrame to normalize it
df_normalized = df.assign(Artist=df['Artist'].str.split(', ')).explode('Artist')

# group by 'Artist' and count distinct titles 
artist_title_counts = df_normalized.groupby('Artist')['Title'].nunique()

# Filter artists with more than one distinct title
filtered_artists = artist_title_counts[artist_title_counts > 1]

# Convert the index (which contains artist names) to a list for the select box options
select_box_options = filtered_artists.index.tolist()

# Sort the list of artists alphabetically, ignoring case
select_box_options_sorted = sorted(select_box_options, key=lambda x: x.lower())



# Populate a selectbox with the sorted artist names
selected_artist = st.selectbox('Select Artist:', select_box_options_sorted)

# Fetch and display data for the selected artist
if selected_artist:
    # Filtering the normalized dataframe for the selected artist
    artist_data = df_normalized[df_normalized['Artist'] == selected_artist]

# Convert 'Date' from string to datetime format
artist_data['Date'] = pd.to_datetime(artist_data['Date'])

# Use the existing 'add_ordinal' function to format the date
def add_ordinal(day):
    return str(day) + ("th" if 4 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th"))

# Format 'Date' as "22nd March, 2024"
artist_data['Formatted_Date'] = artist_data['Date'].dt.day.apply(add_ordinal) + " " + artist_data['Date'].dt.strftime('%B, %Y')

# Get the total followers for each title
total_followers_per_title = artist_data.groupby('Title')['Followers'].sum().reset_index()
    
# Sort the titles by total followers in descending order
sorted_titles = total_followers_per_title.sort_values(by='Followers', ascending=False)['Title']

titles_of_interest = artist_data['Title'].unique()

# Use this order for the x-axis order in the plot
artist_data_filtered = artist_data[artist_data['Title'].isin(titles_of_interest)]

# Stacked bar chart for Reach comparision
fig = px.bar(artist_data_filtered, 
    x='Title', 
    y='Followers', 
    color='Playlist', 
    text='Playlist', 
    custom_data=['Position', 'Formatted_Date'],  # Add 'Formatted_Date' to custom data
    category_orders={'Title': sorted_titles.tolist()})

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

fig.update_xaxes(tickangle=-25)  # Angle can be adjusted as needed

# Customize hover data
fig.update_traces(
    textposition='inside',
    hovertemplate="<b>Release Date:</b> %{customdata[1]}<br>" +  # Access 'Formatted_Date' from custom data
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