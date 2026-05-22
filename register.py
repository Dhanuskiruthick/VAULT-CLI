import bcrypt
import getpass
from database import get_conn

def register_user():
    conn = get_conn()
    cursor = conn.cursor()

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    if len(username) < 3 or len(username) > 20:
        print("Invalid username length")
        return

    if len(password) < 8 or len(password) > 64:
        print("Invalid password length")
        return

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """, (username, hashed.decode()))

        conn.commit()
        print("User registered successfully")

    except Exception:
        print("Username already exists")

    conn.close()
