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
    page_icon=":musical_note:",
    layout="wide"
)
# Title and description
st.title(":radio: Hits Radio - Spotify")
st.markdown("Scrape and analyze songs played on Hits Radio Kenya, with Spotify playlist generation.")
# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    # Time range selection
    st.subheader("Select Time Range")
    time_range_option = st.radio(
        "Choose time range type:",
        ["Last X Hours", "Specific Time Range"]
    )
    if time_range_option == "Last X Hours":
        hours = st.slider("Number of hours to look back:", 1, 24, 3)
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", datetime.strptime("06:00", "%H:%M").time())
        with col2:
            end_time = st.time_input("End Time", datetime.strptime("10:00", "%H:%M").time())
    # Spotify authentication
    st.subheader("Spotify Integration")
    create_playlist = st.checkbox("Create Spotify Playlist", value=False)
    if create_playlist:
        playlist_name = st.text_input(
            "Playlist Name",
            value=f"Hits Radio - {datetime.now().strftime('%Y-%m-%d')}"
        )
        playlist_description = st.text_area(
            "Playlist Description",
            value="A curated list of the latest hits played on Hits Radio Kenya."
        )
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
# Function to filter tracks by time
def filter_tracks(track_list, time_range_option, hours=None, start_time=None, end_time=None):
    if time_range_option == "Last X Hours":
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
    else:
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
# Main app logic
if st.button("Fetch Tracks"):
    with st.spinner("Scraping tracks..."):
        track_list = scrape_radio_tracks()
        # Filter tracks based on selected time range
        if time_range_option == "Last X Hours":
            filtered_tracks = filter_tracks(track_list, time_range_option, hours=hours)
        else:
            filtered_tracks = filter_tracks(track_list, time_range_option,
                                         start_time=start_time, end_time=end_time)
        # Display results
        if filtered_tracks:
            st.success(f"Found {len(filtered_tracks)} tracks!")
            # Convert to DataFrame for display
            df = pd.DataFrame(filtered_tracks)
            st.dataframe(df)
            # Create Spotify playlist if requested
            if create_playlist:
                try:
                    with st.spinner("Creating Spotify playlist..."):
                        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                            redirect_uri="http://localhost:8080/callback",
                            scope="playlist-modify-public"
                        ))
                        # Create playlist
                        user_id = sp.me()['id']
                        playlist = sp.user_playlist_create(
                            user_id,
                            playlist_name,
                            public=True,
                            description=playlist_description
                        )
                        # Search and add tracks
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
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"radio_tracks_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No tracks found in the selected time range.")
# Footer
st.markdown("---")
st.markdown("Made with :heart: using Streamlit. By David Kibet")