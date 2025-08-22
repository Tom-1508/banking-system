import sqlite3

# Connect to SQLite database (creates 'bank.db' if it doesn't exist)
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()   # Cursor is used to execute SQL commands

# Create accounts table if it doesn't exist already
cursor.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique ID for each account
    name TEXT NOT NULL,                     -- Account holder's name
    email TEXT NOT NULL,                    -- Email address
    age INTEGER NOT NULL,                   -- Age of account holder
    pin INTEGER NOT NULL,                   -- PIN for authentication
    account_no TEXT UNIQUE NOT NULL,        -- Unique account number
    balance INTEGER DEFAULT 0               -- Account balance (default = 0)
)
''')

# Save changes and close the connection
conn.commit()
conn.close()
