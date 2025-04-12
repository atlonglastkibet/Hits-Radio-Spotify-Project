import sqlite3

DB_PATH = "hits_radio.db"

def connect_db():
    """Connect to the SQLite database and return connection & cursor."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    return conn, cursor

# Insert new playlist
def insert_playlist(name, description, spotify_playlist_id=None):
    conn, cursor = connect_db()
    cursor.execute("INSERT INTO playlists (name, description, spotify_playlist_id) VALUES (?, ?, ?)", 
                   (name, description, spotify_playlist_id))
    conn.commit()
    conn.close()

# Insert new track
def insert_track(playlist_id, track_name, artist, album, duration, spotify_track_id=None):
    conn, cursor = connect_db()
    cursor.execute("""
        INSERT INTO tracks (playlist_id, track_name, artist, album, duration, spotify_track_id) 
        VALUES (?, ?, ?, ?, ?, ?)""", 
        (playlist_id, track_name, artist, album, duration, spotify_track_id))
    conn.commit()
    conn.close()

# Fetch metrics
def get_metrics():
    conn, cursor = connect_db()
    cursor.execute("SELECT total_playlists, total_tracks_fetched, spotify_users_connected FROM metrics ORDER BY last_updated DESC LIMIT 1")
    metrics = cursor.fetchone()
    conn.close()
    return metrics if metrics else (0, 0, 0)

# Update metrics
def update_metrics():
    conn, cursor = connect_db()
    
    # Count total playlists
    cursor.execute("SELECT COUNT(*) FROM playlists")
    total_playlists = cursor.fetchone()[0]
    
    # Count total tracks
    cursor.execute("SELECT COUNT(*) FROM tracks")
    total_tracks_fetched = cursor.fetchone()[0]
    
    # Count unique Spotify users (assuming each playlist is linked to one user)
    cursor.execute("SELECT COUNT(DISTINCT spotify_playlist_id) FROM playlists WHERE spotify_playlist_id IS NOT NULL")
    spotify_users_connected = cursor.fetchone()[0]
    
    # Update metrics table
    cursor.execute("""
        INSERT INTO metrics (total_playlists, total_tracks_fetched, spotify_users_connected, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
        (total_playlists, total_tracks_fetched, spotify_users_connected))
    
    conn.commit()
    conn.close()
