import time
import hashlib
import bcrypt

def run_speed_test():
    print("\nSHA256 Test Running...")
    start = time.time()

    for i in range(100000):
        hashlib.sha256(f"test{i}".encode()).hexdigest()

    print("SHA256 Time:", time.time() - start)

    print("\nBCRYPT Test Running...")
    start = time.time()

    for i in range(10):
        bcrypt.hashpw(f"test{i}".encode(), bcrypt.gensalt())

    print("BCRYPT Time:", time.time() - start)
