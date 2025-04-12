import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("hits_radio.db")
cursor = conn.cursor()

# Create Playlists Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    spotify_playlist_id TEXT
)
""")

# Create Tracks Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER,
    track_name TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    duration INTEGER,
    spotify_track_id TEXT,
    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE
)
""")

# Create Metrics Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_playlists INTEGER DEFAULT 0,
    total_tracks_fetched INTEGER DEFAULT 0,
    spotify_users_connected INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert initial metrics data if empty
cursor.execute("SELECT COUNT(*) FROM metrics")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO metrics (total_playlists, total_tracks_fetched, spotify_users_connected) VALUES (0, 0, 0)")

# Commit and close
conn.commit()
conn.close()

print("Database setup complete!")
