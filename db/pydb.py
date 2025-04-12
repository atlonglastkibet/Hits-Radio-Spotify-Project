import sqlite3

conn = sqlite3.connect("hits_radio.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(playlists);")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
