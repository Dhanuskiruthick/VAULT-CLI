import sqlite3
import bcrypt
import getpass

conn = sqlite3.connect("vault.db")
cursor = conn.cursor()

username = input("Enter username: ")

password = getpass.getpass("Enter password: ")

# USERNAME VALIDATION
if len(username) < 3:
    print("Username too short!")
    exit()

if len(username) > 20:
    print("Username too long!")
    exit()


# PASSWORD VALIDATION
if len(password) < 8:
    print("Password must be at least 8 characters!")
    exit()

if len(password) > 64:
    print("Password too long!")
    exit()

hashed_password = bcrypt.hashpw(
    password.encode(),
    bcrypt.gensalt()
)

cursor.execute(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    (username, hashed_password.decode())
)

conn.commit()

print("User registered successfully!")