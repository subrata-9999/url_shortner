# # at top of app/main.py (or where you have SessionMiddleware)
# import os
# from dotenv import load_dotenv
# from fastapi import FastAPI
# from app.routers import url_router, user_router
# from app.core.database import Base, engine
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi.staticfiles import StaticFiles


# load_dotenv()
# SECRET = os.getenv("SESSION_SECRET", "supersecretkey123")



# # Base.metadata.create_all(bind=engine)

# app = FastAPI(title="URL Shortener")
# app.add_middleware(SessionMiddleware, secret_key=SECRET)

# # 🔐 Secret key for session encryption
# # app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")
# app.mount("/static", StaticFiles(directory="app/static"), name="static")
# # app.include_router(frontend_router.router)
# app.include_router(user_router.router)
# app.include_router(url_router.router)

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.routers import url_router, user_router
from app.core.database import Base, engine
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
SECRET = os.getenv("SESSION_SECRET", "supersecretkey123")

app = FastAPI(title="URL Shortener")
app.add_middleware(SessionMiddleware, secret_key=SECRET)

# Include routers
app.include_router(user_router.router)
app.include_router(url_router.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "URL Shortener API", "status": "running"}

# Serve static files (if needed)
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    static_file = f"app/static/{file_path}"
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"error": "File not found"}