import sqlite3

def init_db():
    conn = sqlite3.connect('radio_tracks.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            track_title TEXT,
            track_id TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()