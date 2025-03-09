import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Hits Radio - Spotify",
    page_icon=":radio:",
    layout="wide"
)

st.title(":radio: Hits Radio - Spotify")
st.markdown("Your Favourite Radio Hits to Spotify Playlist. Easy!")

# Static metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Playlists", "32")
col2.metric("Total Tracks Fetched", "6,500+")
col3.metric("Spotify Users Connected", "2")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    # Playlist selection
    st.subheader("Select Playlist Type")
    playlist_option = st.selectbox(
        "Choose playlist type:",
        ["Custom Range", "Last X Hours", "Top 50 on Radio", "Morning Hits", "Evening Hits"]
    )
    
    if playlist_option == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", datetime.strptime("06:00", "%H:%M").time())
        with col2:
            end_time = st.time_input("End Time", datetime.strptime("10:00", "%H:%M").time())
    elif playlist_option == "Last X Hours":
        hours = st.slider("Number of hours to look back:", 1, 24, 3)
    
    # Set default playlist name based on the selected playlist option
    if playlist_option == "Top 50 on Radio":
        default_playlist_name = f"Hits Radio Top 50 ({datetime.now().strftime('%Y-%m-%d')})"
    elif playlist_option == "Morning Hits":
        default_playlist_name = f"Hits Radio Morning ({datetime.now().strftime('%Y-%m-%d')})"
    elif playlist_option == "Evening Hits":
        default_playlist_name = f"Hits Radio Evening ({datetime.now().strftime('%Y-%m-%d')})"
    elif playlist_option == "Custom Range":
        default_playlist_name = f"Hits Radio Custom Range ({datetime.now().strftime('%Y-%m-%d')})"
    elif playlist_option == "Last X Hours":
        default_playlist_name = f"Hits Radio Last {hours} Hours ({datetime.now().strftime('%Y-%m-%d')})"
    
    # Spotify authentication
    st.subheader("Spotify Integration")
    create_playlist = st.checkbox("Create Spotify Playlist", value=False)
    if create_playlist:
        playlist_name = st.text_input(
            "Playlist Name",
            value=default_playlist_name
        )
        playlist_description = st.text_area(
            "Playlist Description",
            value="A curated list of the latest hits played on Hits Radio Kenya."
        )
# Custom CSS for a subtle Now Playing section
st.markdown("""
<style>
    .subtle-now-playing {
        border-left: 3px solid #1DB954;  /* Subtle Spotify green border */
        padding-left: 10px;
        margin: 10px 0;
    }
    .subtle-header {
        font-size: 14px;
        color: #888888;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
    }
    .subtle-title {
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 2px;
    }
    .subtle-time {
        font-size: 12px;
        color: #888888;
    }
    .subtle-none {
        font-size: 12px;
        color: #888888;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

def scrape_live_tracks():
    url = 'https://onlineradiobox.com/ke/hitskenya/playlist/?cs=ke.xfmkenya'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        def get_tracks(soup):
            return soup.find_all('a', class_='ajax', href=lambda x: x and x.startswith('/track'))
        
        def get_time(soup):
            return soup.find_all('span', class_='time--schedule')
        
        tracks = get_tracks(soup)
        times = get_time(soup)
        
        track_list = []
        live_track = None
        
        for track, t in zip(tracks, times):
            track_info = {
                "Time": t.text.strip(),
                "Track Title": track.text.strip(),
                "Track ID": track.get('href').split('/track/')[-1].strip('/')
            }
            
            if track_info["Time"] == "Live":
                live_track = track_info
            else:
                track_list.append(track_info)
        
        return track_list, live_track
        
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Error fetching track data. Please try again later.")
        return [], None
    except Exception as e:
        st.sidebar.error(f"Unexpected error occurred. Please try again later.")
        return [], None

# Display the Now Playing section in sidebar
st.sidebar.markdown(
    """
    <div class="subtle-now-playing">
        <div class="subtle-header">
            <span>🎵 &nbsp;Now Playing</span>
        </div>
    """, 
    unsafe_allow_html=True
)

# Get track information
track_list, now_playing = scrape_live_tracks()

if now_playing:
    st.sidebar.markdown(
        f"""
        <div class="subtle-title">{now_playing['Track Title']}</div>
        <div class="subtle-time">Live</div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        """
        <div class="subtle-none">
            No track currently playing.
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown("""
<style>
    /* Base styles for links */
    a {
        text-decoration: none !important;
    }
    
    /* Playlist tile styles */
    .playlist-tile {
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        height: 150px;
        width: 100%;
        transition: transform 0.3s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 20px;
        position: relative;
    }
    .playlist-tile:hover {
        transform: scale(1.01);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    .playlist-name {
        font-weight: bold;
        font-size: 18px;
        color: #ffffff;
        margin-top: auto;
        padding: 0 10px;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.5);
    }

    .spotify-logo {
        font-size: 24px;
        margin-top: 15px;
        color: #ffffff;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.5);
    }

    .playlist-description {
        font-size: 12px;
        color: #f0f0f0;
        margin-top: 5px;
        margin-bottom: 15px;
        text-shadow: 0px 1px 2px rgba(0,0,0,0.4);
    }

    /* Static Gradients */
    .gradient-top50 {
        background: linear-gradient(135deg, #1A924A, #0C6257);  
    }

    .gradient-morning {
        # background: linear-gradient(135deg, #D97873, #CC9A06); 
        # background: linear-gradient(135deg, #B35752, #A37A05);
        background: linear-gradient(135deg, #933E3A, #805E04);
    }

    .gradient-evening {
        background: linear-gradient(135deg, #512DA8, #303F9F);
    }
</style>
""", unsafe_allow_html=True)

# Playlist data with descriptions and gradient classes
recent_playlists = [
    {
        "name": "TOP 50 WKLY",
        "description": "The hottest tracks right now",
        "link": "https://open.spotify.com/playlist/7LSQpp4S4ra24LP3DnuRCF?si=OgmXu0R1T8-jI-0QLaQROA",
        "gradient_class": "gradient-top50"
    },
    {
        "name": "6AM IN WAIYAKI WAY",
        "description": "Watch matatus create lane 8 of 4",
        "link": "https://open.spotify.com/playlist/0WP47PDbhYNS722e5ClNzs?si=xG2OMEvpS4GErsOFmCjeZQ",
        "gradient_class": "gradient-morning"
    },
    {
        "name": "NAIROBI NIGHTS",
        "description": "Relax and unwind after sunset",
        "link": "https://open.spotify.com/playlist/3ak0VoL6g3cIOisGgUQczW?si=bln3amu2Rv-QdZbnA5QCww",
        "gradient_class": "gradient-evening"
    }
]

st.markdown("## Discover Playlists")
st.write("Popular playlists updated weekly!")

# Spotify logo SVG
spotify_svg = """
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fill-rule="evenodd" clip-rule="evenodd" d="M12 0C5.37258 0 0 5.37258 0 12C0 18.6274 5.37258 24 12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0ZM17.2733 17.1656C17.0033 17.5862 16.4082 17.7042 15.9827 17.4333C12.9772 15.5438 9.09845 15.1639 4.73256 16.3683C4.24847 16.5038 3.8467 16.1975 3.74555 15.7303C3.6444 15.2631 3.94992 14.8519 4.43269 14.7212C9.20771 13.3493 13.4667 13.7783 16.9451 15.8953C17.3732 16.1585 17.5406 16.745 17.2733 17.1656ZM18.6768 13.8226C18.3549 14.3436 17.6519 14.5098 17.1308 14.188C14.1612 12.3531 9.48616 11.6513 5.4483 12.8661C4.89285 13.0258 4.39594 12.7178 4.22715 12.1641C4.05837 11.6103 4.37415 11.0753 4.9276 10.9104C9.41883 9.58364 14.6123 10.3585 18.0523 12.4878C18.5734 12.8096 18.8425 13.3017 18.6768 13.8226ZM19.0779 10.3177C15.7379 8.21394 8.67387 7.78389 5.41042 8.88363C4.83732 9.0739 4.20927 8.72968 4.01409 8.15567C3.81892 7.58166 4.16426 6.95176 4.73736 6.7615C8.41189 5.55269 16.0743 6.01797 20.0215 8.38462C20.5389 8.69804 20.7377 9.30983 20.4273 9.82418C20.1169 10.3385 19.5087 10.5439 19.0779 10.3177Z" fill="#F8F8FF"/>
</svg>
"""

# Create a grid of columns for the playlist tiles
cols = st.columns(3)

# Display playlists in the grid
for i, playlist in enumerate(recent_playlists):
    with cols[i % 3]:  # Ensures playlists distribute evenly across 3 columns
        html = f"""
        <a href="{playlist['link']}" target="_blank" class="playlist-tile {playlist['gradient_class']}">
            <div class="spotify-logo">{spotify_svg}</div>
            <div>
                <div class="playlist-name">{playlist['name']}</div>
                <div class="playlist-description"><strong>{playlist['description']}<strong></div>
            </div>
        </a>
        """
        st.markdown(html, unsafe_allow_html=True)


# Close the container div
st.sidebar.markdown("</div>", unsafe_allow_html=True)
# Main function to scrape tracks
def scrape_radio_tracks():
    url = 'https://onlineradiobox.com/ke/hitskenya/playlist/?cs=ke.xfmkenya'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    
    def get_tracks(soup):
        return soup.find_all('a', class_='ajax', href=lambda x: x and x.startswith('/track'))
    
    def get_time(soup):
        return soup.find_all('span', class_='time--schedule')
    
    tracks = get_tracks(soup)
    times = get_time(soup)
    track_list = []
    for track, t in zip(tracks, times):
        track_list.append({
            "Time": t.text.strip(),
            "Track Title": track.text.strip(),
            "Track ID": track.get('href').split('/track/')[-1].strip('/')
        })
    return track_list

# Function to filter tracks by time range
def filter_tracks_by_time_range(track_list, start_time, end_time):
    filtered_tracks = []
    for track in track_list:
        track_time = track["Time"]
        if track_time == "Live":
            continue
        try:
            track_dt = datetime.strptime(track_time, "%H:%M").time()
            if start_time <= track_dt <= end_time:
                filtered_tracks.append(track)
        except ValueError:
            continue
    return filtered_tracks

# Function to get top 50 tracks
def get_top_50_tracks(track_list):
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=24)
    track_counts = {}
    track_details = {}
    
    for track in track_list:
        track_time = track["Time"]
        if track_time == "Live":
            track_time = current_time.strftime("%H:%M")
        try:
            track_dt = datetime.strptime(track_time, "%H:%M").time()
            track_full_dt = datetime.combine(current_time.date(), track_dt)
            if track_full_dt >= cutoff_time:
                track_title = track["Track Title"]
                if track_title in track_counts:
                    track_counts[track_title] += 1
                else:
                    track_counts[track_title] = 1
                    track_details[track_title] = track
        except ValueError:
            continue
    
    sorted_tracks = sorted(track_counts.items(), key=lambda x: x[1], reverse=True)[:50]
    top_50_tracks = [track_details[title] for title, _ in sorted_tracks]
    return top_50_tracks

# Function to filter tracks by last X hours
def filter_tracks_by_last_hours(track_list, hours):
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=hours)
    filtered_tracks = []
    for track in track_list:
        track_time = track["Time"]
        if track_time == "Live":
            track_time = current_time.strftime("%H:%M")
        try:
            track_dt = datetime.strptime(track_time, "%H:%M").time()
            track_full_dt = datetime.combine(current_time.date(), track_dt)
            if track_full_dt >= cutoff_time:
                filtered_tracks.append(track)
        except ValueError:
            continue
    return filtered_tracks

st.markdown("## Create Your Own")
st.write("Customize your playlist just the way you like it!")

# Main app logic
if st.button("Fetch Tracks"):
    with st.spinner("Scraping tracks..."):
        track_list = scrape_radio_tracks()
        
        if playlist_option == "Top 50 on Radio":
            filtered_tracks = get_top_50_tracks(track_list)
        elif playlist_option == "Morning Hits":
            start_time = datetime.strptime("06:00", "%H:%M").time()
            end_time = datetime.strptime("10:00", "%H:%M").time()
            filtered_tracks = filter_tracks_by_time_range(track_list, start_time, end_time)
        elif playlist_option == "Evening Hits":
            start_time = datetime.strptime("16:00", "%H:%M").time()
            end_time = datetime.strptime("19:00", "%H:%M").time()
            filtered_tracks = filter_tracks_by_time_range(track_list, start_time, end_time)
        elif playlist_option == "Custom Range":
            filtered_tracks = filter_tracks_by_time_range(track_list, start_time, end_time)
        elif playlist_option == "Last X Hours":
            filtered_tracks = filter_tracks_by_last_hours(track_list, hours)
        
        # Display results
        if filtered_tracks:
            st.success(f"Found {len(filtered_tracks)} tracks!")
            df = pd.DataFrame(filtered_tracks)
            st.dataframe(df)
            
            if create_playlist:
                try:
                    with st.spinner("Creating Spotify playlist..."):
                        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                            redirect_uri="http://localhost:8080/callback",
                            scope="playlist-modify-public"
                        ))
                        user_id = sp.me()['id']
                        playlist = sp.user_playlist_create(
                            user_id,
                            playlist_name,
                            public=True,
                            description=playlist_description
                        )
                        track_uris = []
                        for track in filtered_tracks:
                            results = sp.search(q=track["Track Title"], type='track', limit=1)
                            if results['tracks']['items']:
                                track_uris.append(results['tracks']['items'][0]['uri'])
                        if track_uris:
                            sp.playlist_add_items(playlist['uri'], track_uris)
                            st.success(f"Created playlist '{playlist_name}' with {len(track_uris)} tracks!")
                        else:
                            st.warning("No tracks were found on Spotify.")
                except Exception as e:
                    st.error(f"Error creating Spotify playlist: {str(e)}")
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"radio_tracks_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No tracks found in the selected time range.")

st.markdown("""
#### **How to Use:**  
1. **Choose a Playlist** – Select from curated options in the sidebar: *Top 50 Hits, Morning Hits, Evening Hits.*  
2. **Personalize It** – Configure additional settings (e.g., time range) to tailor your playlist.  
3. **Fetch Tracks** – Click the *"Fetch Tracks"* button to scrape songs.  
4. **Sync with Spotify (Optional)** – Check *"Create Spotify Playlist"*, enter a name & description.  
5. **Download (Optional)** – Save your fetched tracks as a CSV file.  
""")

# Footer
st.markdown("---")
st.markdown("Made using Streamlit. David Kibet.")