import time
import bcrypt
import getpass
import logging
from database import get_conn

logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def login_user():
    conn = get_conn()
    cursor = conn.cursor()

    username = input("Username: ")
    password = getpass.getpass("Password: ")

    cursor.execute("""
    SELECT password_hash, failed_attempts, lock_until
    FROM users WHERE username = ?
    """, (username,))

    result = cursor.fetchone()

    fake_hash = bcrypt.hashpw(b"fake", bcrypt.gensalt())

    if not result:
        bcrypt.checkpw(password.encode(), fake_hash)
        print("Invalid credentials")
        return

    stored_hash, failed_attempts, lock_until = result
    current_time = int(time.time())

    if lock_until and current_time < lock_until:
        print("Account locked. Try later.")
        logging.warning(f"LOCKED USER={username}")
        return

    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        cursor.execute("""
        UPDATE users
        SET failed_attempts = 0, lock_until = 0
        WHERE username = ?
        """, (username,))

        conn.commit()

        print("Login successful")
        logging.info(f"LOGIN_SUCCESS USER={username}")

    else:
        failed_attempts += 1

        if failed_attempts >= 3:
            lock_until = current_time + 60
            print("Account locked for 60 seconds")

        cursor.execute("""
        UPDATE users
        SET failed_attempts = ?, lock_until = ?
        WHERE username = ?
        """, (failed_attempts, lock_until, username))

        conn.commit()

        print("Invalid credentials")
        logging.warning(f"LOGIN_FAILED USER={username}")

    conn.close()
