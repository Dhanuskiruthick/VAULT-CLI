import sqlite3
import os
print(os.getcwd())
print(os.path.abspath("vault.db"))

conn = sqlite3.connect("vault.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE users
ADD COLUMN failed_attempts INTEGER DEFAULT 0
""")

cursor.execute("""
ALTER TABLE users
ADD COLUMN lock_until INTEGER DEFAULT 0
""")

conn.commit()

print("Migration successful!")