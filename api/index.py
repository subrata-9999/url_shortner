# # api/index.py
# from app.main import app as fastapi_app

# app = fastapi_app

# api/index.py
from mangum import Mangum
from app.main import app as fastapi_app

handler = Mangum(fastapi_app)