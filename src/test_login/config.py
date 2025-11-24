import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")  # neon connection string
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret")
    JWT_REFRESH_SECRET: str = os.getenv("JWT_REFRESH_SECRET", "superrefresh")
    ACCESS_EXPIRE_MINUTES: int = 1
    REFRESH_EXPIRE_DAYS: int = 30

settings = Settings()
