from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv
load_dotenv()
RESET_SECRET = os.getenv("RESET_PASSWORD_SECRET","RESET_SECRET")
RESET_EXPIRE = int(os.getenv("RESET_PASSWORD_EXPIRE_MINUTES", 30))

def create_reset_token(email: str):
    expire_time = datetime.utcnow() + timedelta(minutes=RESET_EXPIRE)
    payload = {"sub": email, "exp": expire_time}
    return jwt.encode(payload, RESET_SECRET, algorithm="HS256")

def verify_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, RESET_SECRET, algorithms=["HS256"])
        return payload.get("sub")  # return only email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")

