from fastapi import Header, HTTPException, Depends
from jose import jwt
from src.test_login.config import settings
from sqlalchemy import select
from src.test_login.database import SessionLocal
from src.test_login.models import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Expect format: Bearer <token>
        token = authorization.credentials
        scheme = authorization.scheme
        if scheme.lower() != "bearer":
            raise Exception("Invalid token format")
        
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("user_id")

        async with SessionLocal() as session:
            stmt = select(User).where(User.id == user_id)
            user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
