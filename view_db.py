import sqlite3 

conn = sqlite3.connect("vault.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for row in users:
    print(row)