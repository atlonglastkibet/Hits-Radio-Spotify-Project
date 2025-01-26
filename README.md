# Hits Radio Spotify Playlist Automation 🎵  
- This project scrapes the latest tracks from [Hits Radio](https://onlineradiobox.com/ke/hitskenya/playlist/?cs=ke.xfmkenya), matches them on **Spotify**, using **Spotify API** and creates a playlist automatically! 
- This project allows you to convert your favorite music station playlist into a Spotify playlist, so you never miss out.
- Here is a [Spotify Playlist](https://open.spotify.com/playlist/6lUOYHk2oISj9P2bgZwzmA?si=xFFGfl_ETuuo1rPYnoRCTQ) link for a Sunday Morning (6-10AM) Hits Radio playlist created on January 26, 2025.
  
## Features 
- **Scrape Tracks**: Fetch the latest tracks played on **Hits Radio** in real time.
- **Spotify Matching**: Automatically match scraped tracks on Spotify using the Spotify API.
- **Playlist Creation**: Create a Spotify playlist with the matched tracks.
- **Customizable**: Specify the number of hours to scrape and the output format (CSV or Spotify playlist).
- **Exploratory Data Analysis (EDA)**: I provide csv outputs to provide insights into trending hits.

## Installation 
1. **Clone the repository**:
   ```bash
   https://github.com/atlonglastkibet/Hits-Radio-Spotify-Project.git

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   
3. **Set up Spotify API credentials**:
    - Create a Spotify Developer account and register an app to get your *SPOTIFY_CLIENT_ID* and *SPOTIFY_CLIENT_SECRET*.
    - Add these credentials to a .env file:
     ```bash
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret

## Usage 
1. Run the Notebook cells
2. Options
  - Hours: Recent number of hours to scrape tracks from (default: 1).
  ```
  get_recent_tracks(track_list, hours=1)
  ```
  - Time range: Range of time in 24 hours to scrape from(default: 6-10AM)
  ```bash
  start_time_x = '06:00' 
  end_time_y = '10:00'
  get_tracks_in_range(track_list, start_time_x,end_time_y)
  ```
3. Output: Output file for the scraped tracks with timestamp.
  ```bash
  CSV file saved to reports/Recent_3H_tracks_2025-01-26_16:41:52.csv
  CSV file saved to reports/Time_range_06:00-10:00H_tracks_2025-01-26_19:14:41.csv
  ```
## How It Works 
1. **Scraping**:
- The script scrapes the Hits Radio playlist page to fetch the latest tracks and their metadata (title, artist, and time played).

2. **Spotify Matching**:
- The script uses the Spotify API to search for each track and match it with the correct song on Spotify.
  
3. **Playlist Creation**:
- Once the tracks are matched, the app creates a Spotify playlist with the matched songs.

## The Search algorithm
- To match scraped tracks with songs on Spotify, this project uses a combination of **Spotify's Search API** and **fuzzy string matching**:

### a. **Spotify Search API**
   - This project uses the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) to search for tracks and artists.
   - The API allows querying by track name, artist, and other metadata.
   - The API returns a list of matching tracks, which are then processed to find the best match.

### b. **Fuzzy String Matching**
   - To handle variations in track and artist names (e.g., typos, abbreviations, or different formats), this project uses **fuzzy string matching** with the `thefuzz` library.
   - Fuzzy matching calculates the similarity between two strings (e.g., the scraped track name and the Spotify track name) and assigns a score.
   - Example:
     ```python
     from thefuzz import fuzz
     similarity_score = fuzz.ratio("You re the One", "You're the One")  # Returns 95
     ```
   - This ensures that even if the scraped data isn't perfectly formatted, the app can still find the correct track on Spotify.
   - In this project I use a similarity score of 70.

### c. **Normalization**
- To ensure accurate matching between scraped tracks and Spotify songs, the app performs **text normalization**:
  1. **Lowercasing**: Convert text to lowercase for case-insensitive matching.
  2. **Remove Diacritics**: Strip accents (e.g., `é` → `e`).
  3. **Remove Special Characters**: Strip punctuation and symbols.
  4. **Remove Common Words**: Remove terms like "Remix", "Live", or "feat.".
  5. **Whitespace Normalization**: Replace multiple spaces with a single space.
   
This ensures consistent formatting and improves matching accuracy.

### d. **Advanced Matching Logic**
   - The app combines **exact matches** and **fuzzy matches** to improve accuracy:
     1. **Exact Match**: If the scraped track name and artist name match exactly with a Spotify track, it’s considered a perfect match.
     2. **Fuzzy Match**: If no exact match is found, the app uses fuzzy matching to find the closest match based on a similarity threshold (e.g., 70% or higher).
     3. **Weighted Scoring**: The app prioritizes artist name matches over track name matches to reduce false positives.

### e. **Workflow**:
1. Scrape a track: `"RockstaMade - Playboi Carti"` from the radio station's playlist.
2. Query Spotify: Search for `"track:RockstarMade artist:Playboi Carti"`.
3. If no exact match is found, use fuzzy matching to find the closest match (e.g., '`"Rockstar Made: Playboi Carti"`).
4. Add the matched track to the Spotify playlist.

- Combining **Spotify's Search API** and **fuzzy string matching** improves accuracy in matching tracks, even when the scraped data isn't perfect.

### Recommendations
- Fine tuning the search algorithm to improve accuracy.
- Bundling the application into a web application so it can run autonomously, along with a GUI for user interaction.
- Adding osuport for more radio stations,allowing users to chose from their favourite raadio station.
- Error handling and action logging for easy debugging and troubleshooting.

## I welcome contributions and feedback!













