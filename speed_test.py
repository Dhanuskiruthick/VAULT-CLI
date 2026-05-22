import hashlib
import bcrypt
import time

#===========================
# SHA256 TEST
#===========================

start = time.time()

for i in range(100000):
    hashlib.sha256(f"password{i}".encode()).hexdigest()

end = time.time()

print("\nSHA256 Time: ")
print(end - start)


#===========================
# BCRYPT TEST   
#===========================

start = time.time()

for i in range(10):  # bcrypt is much slower than sha256, so we will do only 10 iterations to keep the test reasonable
    bcrypt.hashpw(f"password{i}".encode(), bcrypt.gensalt())

end = time.time()

print("\nBCRYPT Time: ")
print(end - start)