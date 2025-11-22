from fastapi import FastAPI
from src.test_login.auth.routes import router as auth_router
from src.test_login.models import Base
from src.test_login.database import engine
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ElectroSoft Auth API")

# --------------------------------------------------
# GLOBAL CORS (ALLOW ALL)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all domains
    allow_credentials=True,
    allow_methods=["*"],       # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],       # allow all headers including Authorization
)
# --------------------------------------------------

# @app.on_event("startup")
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router)


@app.get("/")
def home():
    return {"message": "ElectroSoft API running"}
