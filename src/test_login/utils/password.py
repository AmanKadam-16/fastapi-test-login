from passlib.context import CryptContext

# pwd = CryptContext(schemes=["argon2"], deprecated="auto")
pwd = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd.verify(raw, hashed)
