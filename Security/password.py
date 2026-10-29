from pwdlib import PasswordHash

pwd = PasswordHash.recommended()

def hash_password(password):
    return pwd.hash(password)

def verify_password(password, hashed):
    return pwd.verify(password, hashed)