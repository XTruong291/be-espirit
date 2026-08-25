import jwt
from datetime import datetime, timedelta, timezone
#cấu hình secret key và thời hạn token
SECRET_KEY = "your-secret-key-keep-it-secret"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  

def get_password_hash(password: str) -> str:
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return f"hashed_{plain_password}" == hashed_password

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt