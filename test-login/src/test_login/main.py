from fastapi import FastAPI
from src.test_login.auth.routes import router as auth_router
from src.test_login.models import Base
from src.test_login.database import engine

app = FastAPI(title="ElectroSoft Auth API")

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "ElectroSoft API running"}
