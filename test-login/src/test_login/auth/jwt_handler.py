from datetime import datetime, timedelta
from jose import jwt
from src.test_login.config import settings

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, settings.JWT_REFRESH_SECRET, algorithm="HS256")

def verify_refresh_token(token: str):
    return jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
