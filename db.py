import sqlite3

conn = sqlite3.connect("blockchain.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT
)
""")

def add_block(data):
    cursor.execute("INSERT INTO blocks (data) VALUES (?)", (str(data),))
    conn.commit()

def get_blocks():
    cursor.execute("SELECT * FROM blocks")
    return cursor.fetchall()