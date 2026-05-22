import sqlite3
import time
import bcrypt
import getpass
import logging
import os
print(os.getcwd())
print(os.path.abspath("vault.db"))

logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

conn = sqlite3.connect("vault.db")

cursor = conn.cursor()

#Login system
username = input("Username: ")
password = getpass.getpass("Password: ")

cursor.execute(
    "SELECT password_hash , failed_attempts , lock_until FROM users WHERE username = ?",
    (username,)
)

result = cursor.fetchone()

#Fake hash for taking consistency 
fake_hash = bcrypt.hashpw(b"fake", bcrypt.gensalt())

if result is None:
    # still run bcrypt to avoid timing leak
    bcrypt.checkpw(password.encode() , fake_hash)
    print("Invalid Credentials :( ")
else:
    stored_hash ,failed_attempts , lock_until = result
    stored_hash = stored_hash.encode()  # Convert to bytes

    current_time = int(time.time())

    #CHECK LOCK
    if lock_until and current_time < lock_until:
        print("Account is locked . Try again later :( ")
        logging.warning(f"ACCOUNT_LOCKED USER={username}")
        exit()

    #VERIFY PASSWORD    
    if bcrypt.checkpw(password.encode(), stored_hash):

        #RESET on SUCCESS
        cursor.execute(
            "UPDATE users SET failed_attempts = 0 , lock_until = 0 WHERE username = ?",
            (username,)
        )  
        conn.commit() 
        print("Login successful!")
        logging.info(f"LOGIN_SUCCESS USER={username}")
    else:
        failed_attempts +=1

        #LOCK RULE ( after 3 attempts)
        if failed_attempts >= 3:
            lock_time = current_time + 60   # 1 minute lock

            cursor.execute(
                "UPDATE users SET failed_attempts = ? , lock_until = ? WHERE username = ?",
                (failed_attempts , lock_time , username) 
                )
            
        else:
            cursor.execute(
                "UPDATE users SET failed_attempts = ? WHERE username = ?",
                (failed_attempts, username)
            )

        conn.commit()
        print("Invalid Credentials :( ") 
        logging.warning(f"LOGIN_FAILED USER={username}")   