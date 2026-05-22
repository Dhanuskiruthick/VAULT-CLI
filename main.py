import bcrypt

password = "mypassword12345"

hashed = bcrypt.hashpw(

    password.encode(),
    bcrypt.gensalt()
)

print(hashed)
