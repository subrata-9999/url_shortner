import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    MAX_REQUEST_SIZE: int = 10

settings = Settings()
