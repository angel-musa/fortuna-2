import sqlite3

# Initialize or connect to the SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create a table to store user data
c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                watchlist TEXT
            )''')
conn.commit()
conn.close()
