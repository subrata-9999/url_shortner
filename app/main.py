# at top of app/main.py (or where you have SessionMiddleware)
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.routers import url_router, user_router
from app.core.database import Base, engine
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


load_dotenv()
SECRET = os.getenv("SESSION_SECRET", "supersecretkey123")



# Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

# 🔐 Secret key for session encryption
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# app.include_router(frontend_router.router)
app.include_router(user_router.router)
app.include_router(url_router.router)
