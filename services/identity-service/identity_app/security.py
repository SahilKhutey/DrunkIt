import time
import jwt
import bcrypt

SECRET_KEY = "faccp-identity-vault-super-secret-key-32bytes"
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 86400

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = int(time.time())
    to_encode.update({
        "iat": now,
        "exp": now + TOKEN_EXPIRE_SECONDS,
        "iss": "faccp-identity-service"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
