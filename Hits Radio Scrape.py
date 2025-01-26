#!/usr/bin/env python
# coding: utf-8

# ## HITS RADIO SCRAP

# In[ ]:


# - In this project, I'll be scraping Top songs on Hits Radio website: https://onlineradiobox.com/ke/hitskenya/. 
# - I'll be scraping the song name, artist name then searching the songs on spotify and generating a Playlist.
# - I'll be using BeautifulSoup and requests libraries to scrape the website.

# ### Import libraries

# In[74]:


from bs4 import BeautifulSoup
import requests as re


# ### Scrap website

# In[75]:


url = 'https://onlineradiobox.com/ke/hitskenya/playlist/?cs=ke.xfmkenya'
html = re.get(url).text
soup = BeautifulSoup(html, 'html.parser')


# In[76]:


# Here I use the class name 'ajax' to find the songs
songs = soup.find_all('a', class_='ajax')
time = soup.find_all('span', class_='time--schedule')


# In[77]:


# I then develop a function to get the tracks and strip the href
def get_tracks(soup):
    tracks = soup.find_all('a', class_='ajax', href=lambda x: x and x.startswith('/track'))
    return tracks

tracks = get_tracks(soup)

def get_time(soup):
    time = soup.find_all('span', class_='time--schedule')
    return time


# In[78]:


# Here I just print the tracks neatly
for track in get_tracks(soup): #tracks
	print(track.prettify())
for t in get_time(soup): #time
	print(t.prettify())


# In[79]:


# Create an empty list to store track details
track_list = []

# Loop through each track and its corresponding time
for track, t in zip(get_tracks(soup), get_time(soup)):  
    track_title = track.text.strip()  # Extract track title
    track_href = track.get('href')  # Extract the href link
    track_id = track_href.split('/track/')[-1].strip('/')  # Extract track ID
    time = t.text.strip()  # Extract time

    # Store details in a dictionary and append to list
    track_list.append({
        "Time": time,
        "Track Title": track_title,
        "Track ID": track_id
    })

# Print the stored list (optional)
print(track_list)


# In[80]:


# Loop through the list of track details and print each track
for track in track_list:
    print(track)


# In[97]:


import csv
import os
from datetime import datetime

def save_tracks_to_csv(track_list, filename="tracks.csv"):
    """
    Save track list to CSV file with timestamp
    
    :param track_list: List of track dictionaries
    :param filename: Output filename (default: tracks.csv)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Define CSV headers
    fieldnames = ["Track Title", "Time", "Track ID", "Export Timestamp"]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for track in track_list:
                # Add export timestamp and preserve original data
                writer.writerow({
                    "Track Title": track.get("Track Title", ""),
                    "Time": track.get("Time", ""),
                    "Track ID": track.get("Track ID", ""),
                    "Export Timestamp": datetime.now().isoformat()
                })
        print(f"Successfully saved {len(track_list)} tracks to {filename}")
        
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")

    # Save to CSV
    save_tracks_to_csv(track_list, "music_tracks.csv")


# ### Extract music from the last hour, two hours e.t.c

# - First of all we need to get the time range for the whole tracklist

# In[81]:


from datetime import datetime

def get_time_range(track_list):
    """
    Get the earliest and latest times in the track list.
    
    :param track_list: List of dictionaries containing track details and times.
    :return: Tuple of (earliest_time, latest_time) in 'HH:MM' format.
    """
    earliest_time = None
    latest_time = None

    # Loop through the track list to check all times
    for track in track_list:
        track_time = track["Time"]

        # If track_time is 'Live', use the current time
        if track_time == 'Live':
            track_time = datetime.now().strftime("%H:%M")

        try:
            # Convert track time to a datetime object
            track_dt = datetime.strptime(track_time, "%H:%M")

            # Update the earliest and latest times
            if earliest_time is None or track_dt < earliest_time:
                earliest_time = track_dt
            if latest_time is None or track_dt > latest_time:
                latest_time = track_dt
        except ValueError:
            # Skip tracks with invalid time data
            print(f"Skipping track with invalid time data: {track['Track Title']} ({track_time})")

    # Return the times in 'HH:MM' format
    return earliest_time.strftime("%H:%M") if earliest_time else None, latest_time.strftime("%H:%M") if latest_time else None


# In[82]:


print(f'The time range for this tracklist is: {get_time_range(track_list)}')


# - From the last *(amount) hours

# In[83]:


from datetime import datetime, timedelta

def get_recent_tracks(track_list, hours=1):
    """
    Extracts tracks from the last 'hours' from the given track list.
    
    :param track_list: List of dictionaries with keys: "Track Title", "Time", "Track ID".
    :param hours: Number of past hours to filter tracks (default: 1).
    :return: Filtered list of track dictionaries.
    """
    recent_tracks = []
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(hours=hours)

    for track in track_list:
        track_title = track["Track Title"]
        track_time = track["Time"]

        # Handle "Live" as current time
        if track_time == "Live":
            track_time = current_time.strftime("%H:%M")

        try:
            # Parse time without assuming the date
            parsed_time = datetime.strptime(track_time, "%H:%M").time()
            
            # Create candidate datetime for today and yesterday
            today_date = current_time.date()
            candidate_dt_today = datetime.combine(today_date, parsed_time)
            candidate_dt_yesterday = candidate_dt_today - timedelta(days=1)

            # Check which candidate is within the cutoff window
            if candidate_dt_today <= current_time and candidate_dt_today >= cutoff_time:
                valid_dt = candidate_dt_today
            elif candidate_dt_yesterday >= cutoff_time:
                valid_dt = candidate_dt_yesterday
            else:
                continue  # Track is outside the window

            recent_tracks.append({
                "Time": track_time,
                "Track Title": track_title,
                "Track ID": track["Track ID"]
            })

        except ValueError:
            print(f"Skipping invalid time format: {track_title} ({track_time})")

    return recent_tracks


# In[84]:


import csv
import os
from datetime import datetime

def save_recent_tracks_to_csv(recent_tracks, filename="recent_tracks.csv"):
    """
    Save filtered recent tracks to a CSV file with metadata
    
    :param recent_tracks: List of track dictionaries from get_recent_tracks()
    :param filename: Output filename (default: recent_tracks.csv)
    """
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    filepath = os.path.join('reports', filename)
    
    fieldnames = ["Time streamed", "Track Title", "Track ID", "Report Timestamp"]
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for track in recent_tracks:
                # Add current timestamp for the report
                track_with_meta = {
                    **track,
                    "Report Timestamp": datetime.now().isoformat()
                }
                writer.writerow(track_with_meta)
                
        print(f"Successfully saved {len(recent_tracks)} tracks to {filepath}")
        
    except Exception as e:
        print(f"Error saving CSV file: {str(e)}")


# In[85]:


# This are songs played on Hits Radio for the last hour
last_hour = get_recent_tracks(track_list, hours=2)
save_recent_tracks_to_csv(last_hour, "last_hour_tracks.csv")
for tracks_artists in last_hour:
    print(tracks_artists)


# - From a date range 

# In[86]:


from datetime import datetime

def get_tracks_in_range(track_list, start_time, end_time):
    """
    Extracts tracks within a specific time range from the track list.
    
    :param track_list: List of dictionaries containing track details and times.
    :param start_time: Start time in 'HH:MM' format.
    :param end_time: End time in 'HH:MM' format.
    :return: List of dictionaries with track details.
    """
    tracks_in_range = []

    # Convert start and end times to datetime objects
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")

    for track in track_list:
        track_title = track["Track Title"]
        track_time = track["Time"]

        # Check if track_time is 'Live' (currently playing)
        if track_time == 'Live':
            track_time = datetime.now().strftime("%H:%M")  # Convert 'Live' to current time in HH:MM format

        try:
            # Convert track time to a datetime object
            track_dt = datetime.strptime(track_time, "%H:%M")

            # Check if the track falls within the given time range
            if start_dt <= track_dt <= end_dt:
                tracks_in_range.append({
                    "Time": track_time,
                    "Track Title": track_title,
                    "Track ID": track["Track ID"]
                })
        except ValueError:
            # Skip tracks with invalid time data
            print(f"Skipping track with invalid time data: {track_title} ({track_time})")

    return tracks_in_range


# In[87]:


get_tracks_in_range(track_list, '07:00','11:00')


# ### Spotify’s search API expects a query in this format: 'https://api.spotify.com/v1/search?q=<query>&type=track'
# 

# In[88]:


import re

def clean_title(title):
    """Remove noise like (Lyrics), codes, etc."""
    title = re.sub(r'\([^)]*\)|\b\d+.*$', '', title)  # Remove () content and codes
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def parse_tracklist_to_spotify_query(track_list):
    spotify_queries = []
    for track in track_list:
        track_title = track.get("Track Title", "Unknown Title")
        artist = track.get("Artist", "").strip()

        # Clean the title first
        track_title = clean_title(track_title)

        # Extract artist from title if missing
        if not artist:
            # Split by common delimiters (e.g., " - ", "feat", "ft", "&")
            parts = re.split(r'\s+[-–—]+\s+| feat\b| ft\b| & |/', track_title, flags=re.IGNORECASE)
            possible_artist = parts[0].strip() if parts else "Unknown Artist"
            # Allow apostrophes, hyphens, and & in artist names
            possible_artist = re.sub(r'[^a-zA-Z\s\'\-&]', '', possible_artist)
            artist = possible_artist if possible_artist else "Unknown Artist"

        # Extract featured artists from title (e.g., "Song (feat. Artist)")
        featured = re.findall(r'\(feat[.\s]*([^)]+)\)', track_title, re.IGNORECASE)
        if featured:
            featured_artist = re.sub(r'[^a-zA-Z\s\'\-&]', '', featured[0].strip())
            artist += f", {featured_artist}"

        # Final cleanup
        artist = re.sub(r'\s+', ' ', artist).strip()
        query = f"track:{track_title} artist:{artist}"
        spotify_queries.append(query)

    return spotify_queries


# In[89]:


raw_data = parse_tracklist_to_spotify_query(last_hour)
print(raw_data)


# In[90]:


for x in raw_data:
    print(x)


# In[91]:


import re
from thefuzz import fuzz, process
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import unicodedata
import logging


import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://localhost:8080/callback",
    scope="playlist-modify-public"
))

class SpotifyTrackMatcher:
    def __init__(self, sp_client):
        """
        Initialize the Spotify Track Matcher with enhanced search capabilities.
        
        :param sp_client: Authenticated Spotify client
        """
        self.sp = sp_client
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def normalize_text(self, text):
        """
        Comprehensive text normalization:
        1. Convert to lowercase
        2. Remove diacritical marks
        3. Remove extra whitespaces
        4. Handle special characters
        
        :param text: Input text to normalize
        :return: Normalized text
        """
        # Remove diacritical marks
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        
        # Lowercase and remove extra spaces
        return re.sub(r'\s+', ' ', text.lower()).strip()

    def extract_canonical_features(self, title):
        """
        Extract canonical features from track title:
        1. Remove parenthetical info 
        2. Remove common words
        3. Extract core title elements
        
        :param title: Original track title
        :return: Canonical title features
        """
        # Remove parenthetical content and metadata
        title = re.sub(r'\(.*?\)|\[.*?\]', '', title)
        
        # Remove common words and prefixes
        title = re.sub(r'\b(the|a|an|remix|remaster|live)\b', '', title, flags=re.IGNORECASE)
        
        return self.normalize_text(title)

    def advanced_artist_matching(self, track_candidates, search_artist):
        """
        Advanced artist matching with multiple strategies:
        1. Full artist name match
        2. Partial artist name match
        3. Multiple artist combinations
        
        :param track_candidates: List of track candidates
        :param search_artist: Artist search string
        :return: Best matching track
        """
        normalized_search_artist = self.normalize_text(search_artist)
        
        # Split potential multiple artists
        potential_artists = re.split(r'[&,x]|\bft\.|\bfeat\.', search_artist, flags=re.IGNORECASE)
        potential_artists = [self.normalize_text(artist.strip()) for artist in potential_artists]
        
        best_match = None
        best_score = 0
        
        for track in track_candidates:
            # Extract track artists
            track_artists = [self.normalize_text(artist['name']) for artist in track['artists']]
            
            # Score calculation with multiple strategies
            artist_match_score = max([
                max([fuzz.ratio(pa, ta) for ta in track_artists]) 
                for pa in potential_artists
            ])
            
            # Weighted scoring
            track_score = (
                0.6 * artist_match_score + 
                0.4 * fuzz.ratio(
                    self.extract_canonical_features(track['name']),
                    self.extract_canonical_features(search_artist)
                )
            )
            
            if track_score > best_score:
                best_score = track_score
                best_match = track
        
        # Confidence threshold
        return best_match if best_score > 70 else None

    def search_track(self, title, artist, max_results=20):
        """
        Comprehensive track search with multiple fallback strategies
        
        :param title: Track title
        :param artist: Artist name
        :param max_results: Maximum search results to consider
        :return: Best matching track URI or None
        """
        # Normalize inputs
        normalized_title = self.normalize_text(title)
        normalized_artist = self.normalize_text(artist)
        
        # Search strategies in order of specificity
        search_strategies = [
            f"track:{title} artist:{artist}",  # Most specific
            f"track:{normalized_title}",       # Title-only fallback
            f"artist:{normalized_artist}"      # Artist-only fallback
        ]
        
        for strategy in search_strategies:
            try:
                results = self.sp.search(q=strategy, type='track', limit=max_results)
                track_candidates = results['tracks']['items']
                
                if track_candidates:
                    # Advanced matching
                    best_match = self.advanced_artist_matching(track_candidates, artist)
                    
                    if best_match:
                        self.logger.info(f"Matched: {best_match['name']} - {best_match['artists'][0]['name']}")
                        return best_match['uri']
            
            except Exception as e:
                self.logger.error(f"Search error with strategy {strategy}: {e}")
        
        self.logger.warning(f"No match found for {title} by {artist}")
        return None

def parse_and_match_spotify(sp_client, raw_data):
    """
    Process multiple tracks with enhanced matching
    
    :param sp_client: Spotify client
    :param raw_data: Raw track data
    :return: List of matched track URIs
    """
    matcher = SpotifyTrackMatcher(sp_client)
    uris = []
    
    for entry in raw_data:
        try:
            # Split and clean entry similar to original implementation
            title, artist = parse_entry(entry)
            
            uri = matcher.search_track(title, artist)
            if uri:
                uris.append(uri)
        
        except Exception as e:
            matcher.logger.error(f"Error processing entry {entry}: {e}")
    
    return uris

def parse_entry(entry):
    """
    Parse raw entry into title and artist
    
    :param entry: Raw track entry
    :return: Tuple of (title, artist)
    """
    # Implement similar parsing logic to original code
    # This is a placeholder and should match your specific input format
    parts = entry.split("artist:")
    title = parts[0].replace("track:", "").strip()
    artist = parts[1].strip() if len(parts) > 1 else "Unknown"
    
    return title, artist


# In[92]:


track_uris = parse_and_match_spotify(sp, raw_data)
print(f"\nA total of {
    len(track_uris)} out of the {len(raw_data)} played on Radio were matched on Spotify. \nThat's {
        len(track_uris)/len(raw_data)*100:.2F}% of the songs.\n")
# print("Matched URIs:", track_uris)


# In[93]:


# # Create a new playlist
# playlist_name = "Hits Radio Last Hour"
# user_id = sp.me()['id']
# playlist = sp.user_playlist_create(user_id, playlist_name, public=True)

# # Add tracks to the playlist
# sp.playlist_add_items(playlist['uri'], track_uris)

# print(f"Playlist '{playlist_name}' created with {len(track_uris)} tracks!")

