# New Music - Spotify Playlists Tracker (AU) 
## Providing a snapshot of Friday's release performance.   


[New Music Playlist Tracker](https://new-music-playlist-tracker-c480db72347d.herokuapp.com/)


The site pulls all songs added to New Music Friday AU & NZ, and then checks to see if these songs have also been added to any key editorial AU playlists.

This means New Releases that did not get added to NMF AU & NZ will not show up on this site. Focusing on the releases that Spotify has chosen to feature in NMF. 

## List of playlists currently checking: 

#### Spotify AU Editorial Playlists:

| New Music Friday AU & NZ | Fresh Country  | Breaking Hits      |
|--------------------------|----------------|--------------------|
| Top 50 Australia         | New Dance Beats| Chilled Hits       |
| Hot Hits Australia       | Pop n' Fresh   | the hybrid         |
| Front Left               | Beats n' Bars  | Coffee + Chill     |
| A1                       | Indie Arrivals | Gentle Acoustic    |
| Dance Generation         | Rock Out.      |                    |
| Get Popped!              | Mellow Styles  |                    |
| R&B Connect              | The Drip       |                    |
| The Flavour              | Alt Here       |                    |

#### Other Playlists:

|                                |
|--------------------------------|
| triple j's New Music Hitlist   |



-----

### Prerequisites

Before you can run this project locally, make sure you have the following installed:
- Python (3.8 or later)
- pip (Python package manager)
- A Spotify Developer account and API credentials (Client ID and Client Secret). You can create a Spotify Developer account and obtain your API credentials by following the guide [here](https://developer.spotify.com/documentation/web-api/tutorials/getting-started).

----
### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/new-music-playlist-tracker.git
2. **Set up a virtual environment** (Optional)

   Navigate to your project directory:

   ```bash
   cd spotify_au_release_app
   ```

   Create the virtual environment:

   ```bash
   python -m venv venv
   ```

   Activate the virtual environment:

   ```bash
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```


3. **Install required Python packages**

   While in your project directory and with the virtual environment activated, install the dependencies using:

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**

   Create a `.env` file in the root directory of your project and add your Spotify API credentials, and any other necessary configurations. Here's an example template:

   ```plaintext
   CLIENT_ID='your_spotify_client_id'
   CLIENT_SECRET='your_spotify_client_secret'
   ```
---
### Running Locally

To run the project locally, ensure you're in the project root directory and your virtual environment is activated. Then start the application. 
```bash
streamlit run home.py
