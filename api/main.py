from mangum import Mangum
from src.test_login.main import app   # your actual FastAPI app

handler = Mangum(app)
